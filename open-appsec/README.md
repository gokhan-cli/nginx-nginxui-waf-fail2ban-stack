# open-appsec Kurulum ve Yapılandırma Rehberi (Ubuntu 24.04 & Nginx)

Bu doküman, herhangi bir Linux sunucuya (özellikle Ubuntu 24.04) Nginx üzerinde çalışan **open-appsec** eklentisinin nasıl kurulacağını ve "Lokal Yönetim (Local Policy)" moduyla nasıl yapılandırılacağını adım adım açıklar.

> [!important]
> open-appsec, geleneksel kurallı (regex tabanlı) WAF sistemlerinden ziyade Makine Öğrenimi (AI) kullanarak zero-day saldırılarını sıfıra yakın yanılma payıyla engeller. Bu kurulum **Nginx** veya **Nginx Proxy Manager** sistemleri üzerinde çalışmak üzere tasarlanmıştır.

---

## 1. Sistemin Hazırlanması

open-appsec kurulum scriptini çalıştırabilmek için gerekli bazı temel araçları sisteminize yükleyin:
```bash
sudo apt update
sudo apt install -y curl wget wget jq perl bash
```
> Eğer Nginx sunucunuzda önceden kurulu değilse, Nginx'i kurduğunuzdan emin olun (`sudo apt install nginx -y`).

## 2. open-appsec Kurulum Dosyasını (Agent) İndirme

open-appsec'in resmi kurulum aracını internetten çekiyoruz:

```bash
wget https://downloads.openappsec.io/open-appsec-install -O open-appsec-install
chmod +x open-appsec-install
```

## 3. Ajanı (Nano Agent) Nginx İçin Kurma

open-appsec, doğrudan "Local Management" (Yerel Dosya) ile yönetilebilir. Biz bu senaryoda tamamen lokal olarak `local_policy` kullanacağız. 

Aşağıdaki komutlarla önce bağımlılıkları indiriyor, ardından open-appsec'i **Lokal Yönetim (Local Management)** moduyla Nginx eklentisi olarak kuruyoruz:

```bash
# İlk olarak gerekli paketleri(engine) sunucuya indiriyoruz.
sudo ./open-appsec-install --download

# Sonrasında aşağıdaki kütüphaneleri library dizinine kopyalıyoruz.
cp /tmp/open-appsec/ngx_module_1.29.8-1-noble/libshmem_ipc_2.so /usr/lib
cp /tmp/open-appsec/ngx_module_1.29.8-1-noble/libosrc_shmem_ipc.so /usr/lib
cp /tmp/open-appsec/ngx_module_1.29.8-1-noble/libosrc_compression_utils.so /usr/lib
cp /tmp/open-appsec/ngx_module_1.29.8-1-noble/libosrc_nginx_attachment_util.so /usr/lib

# Nginx Attacment dosyasını da nginx modül dizinine kopyalıyoruz.
cp /tmp/open-appsec/ngx_module_1.29.8-1-noble/ngx_cp_attachment_module.so /usr/lib/nginx/modules/ngx_cp_attachment_module.so

# Modülü nginx üzerinde aktif etmek için aşağıdaki komutu yazıp nginx.conf dosyamızın en üstüne ekliyoruz.
sudo sed -i '1s|^|load_module /usr/lib/nginx/modules/ngx_cp_attachment_module.so;\n|' /etc/nginx/nginx.conf
sudo systemctl restart nginx
# Hata almadıysak işlem başarılı olmuş demektir.
# Son olarak aşağıdakileri de çalıştırıyoruz.
/tmp/open-appsec/openappsec/install-cp-nano-agent.sh --install --hybrid_mode --server 'NGINX Server'
/tmp/open-appsec/openappsec/./install-cp-nano-agent-cache.sh --install
/tmp/open-appsec/openappsec/install-cp-nano-service-http-transaction-handler.sh --install
/tmp/open-appsec/openappsec/install-cp-nano-attachment-registration-manager.sh --install
```

Kurulum tamamlandıktan sonra, servislerin sağlığını test etmek için:
```bash
open-appsec-ctl -s
```
*(Tüm servislerin yeşil / çalışan durumda olması beklenir).*

---

## 4. Lokal Politikanın (Local Policy) Yapılandırılması

open-appsec "local" modda çalıştığında, kurallarını `/etc/cp/policy/local_policy.yaml` dosyasından alır. (Bu dosya yoksa el ile oluşturun).

```bash
sudo nano /etc/cp/conf/local_policy.yaml
```

Dosyanın içerisine örnek bir **Güvenli (Prevent)** WAF politikası yerleştirin:

```yaml
# open-appsec default declarative configuration file
# based on schema version: "v1beta2"
# more information on declarative configuration: https://docs.openappsec.io

apiVersion: v1beta2

policies:
  default:
    # start in detect-learn and move to prevent-learn based on learning progress
    mode: prevent-learn
    threatPreventionPractices: [default-threat-prevention-practice]
    accessControlPractices: [default-access-control-practice]
    customResponses: default-web-user-response
    triggers: [default-log-trigger]
    sourceIdentifiers: ""
    trustedSources: ""
    exceptions: []
  specificRules: []
...
...
    logDestination:
      cloud: false
      logToAgent: true
      stdout:
        format: json

customResponses:
  - name: default-web-user-response
    mode: response-code-only
    httpResponseCode: 403
```

```bash
sudo open-appsec-ctl --apply-policy
```

Son olarak Nginx'i yeniden başlatarak modülün tam güç devreye girmesini sağlayın:
```bash
sudo systemctl restart nginx
```

---

## 6. Test ve Doğrulama Üstüne Entegrasyon

Ajan başarıyla yüklendiğinde; Nginx üzerinden geçen tüm istekler arka planda AI motorundan süzülmeye başlar. 

### A. Test Yapın
Browserınızdan veya curl ile sitenize örnek bir zararlı yük (payload) gönderin:
```bash
curl "http://SUNUCU_IP/?arg=<script>alert('xss')</script>"
```
Sitenin size anında `HTTP 403 Forbidden` veya open-appsec engelleme sayfası döndürmesi gerekir. 

### B. Logların CrowdSec İçin Lokal Dosyaya Düşmesi (Cloud'a Gitmeden)
Yukarıda yazdığımız `logDestination` altında ki `logToAgent: true` politikası sayesinde bulut paneline hiçbir veri gönderilmez, engellenen saldırılar doğrudan şu log dosyasına JSON olarak akar:
```bash
tail -f /var/log/nano_agent/cp-nano-http-transaction-handler.log* | jq .
```
Yukarıdaki log çıktısında `"securityAction": "Prevent"` değerini görüyorsanız her şey mükemmel çalışıyor demektir. 

**🔴 BURASI ÖNEMLİ (CrowdSec Geçişi) 🔴**
open-appsec görevini yapıp bunu yukarıdaki lokal log dosyasına yazdı! Şimdi devredeki **CrowdSec**, önceden kurduğumuz o özel `open-appsec.yaml` parser'ı sayesinde bu lokal dosyayı (offline olarak sunucu içinden) aralıksız okur. Prevent logunu gördüğü saniye ilgili IP adresini bir daha asla sizin Nginx sunucunuza giremeyecek şekilde OS-level (iptables) banlar!
