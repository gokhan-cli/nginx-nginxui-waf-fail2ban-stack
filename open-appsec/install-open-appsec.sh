## 3. OpenAppSec Kurulumu ve WAF Entegrasyonu

# OpenAppSec merkezi bulut (SaaS) yerine tamamen **yerel (local)** olarak yönetilecek ve çalışacaktır. 
# Bu nedenle kurulum, offline entegrasyonu sağlamak adına "download mod" ile ilerleyecektir:

wget https://downloads.openappsec.io/open-appsec-install && chmod +x open-appsec-install 

# OpenAppSec'i yerel yönetim için download modunda çalıştıran komut:
sudo ./open-appsec-install --download # OpenAppSec localde çalışağı için biz bu modu kullanacağız.

#Eğer yukarıdaki script ile kurulumda sorun yaşarsanız, klasör içindeki dosyayı sunucunuza çekip kullanabilirsiniz.
wget https://raw.githubusercontent.com/gokhan-cli/nginx-nginxui-waf-fail2ban-stack/refs/heads/main/open-appsec/open-appsec-install && chmod +x open-appsec-install

# Yine kurulum için aşağıdaki parametreleri kullanacağız.
sudo ./open-appsec-install --download
