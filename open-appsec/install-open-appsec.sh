## 3. OpenAppSec Kurulumu ve WAF Entegrasyonu

# OpenAppSec merkezi bulut (SaaS) yerine tamamen **yerel (local)** olarak yönetilecek ve çalışacaktır. 
# Bu nedenle kurulum, offline entegrasyonu sağlamak adına "download mod" ile ilerleyecektir:

wget https://downloads.openappsec.io/openappsec-install
chmod +x openappsec-install

# OpenAppSec'i yerel yönetim için download modunda çalıştıran komut:
sudo ./openappsec-install --auto # Download modda kurulum aşamasında hata almamak için kurulumu önce bu modda çalıştırın.
sudo ./openappsec-install --download # OpenAppSec yerelde çalışağı için biz bu modu kullanacağız.

# (İndirilen paketi sisteminize göre genişleterek kurulum dosyasından
# yerel yönetim (Local Management / Declarative) seçeneğiyle entegrasyonu tamamlayın.)
# *(Not: Kurulum download modunda ve tamamen "local" yapıldığından,
# WAF konfigürasyonunuz ve tespit kurallarınız sunucunuz üzerindeki yerel politika dosyası (`local_policy.yaml`) aracılığıyla yönetilecektir. Entegrasyon tamamlandığında eklenti `nginx.conf` içerisine gömülecektir.)*
