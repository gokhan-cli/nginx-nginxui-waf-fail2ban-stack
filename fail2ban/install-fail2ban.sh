sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

git clone https://github.com/KULLANICI_ADINIZ/nginx-nginxui-waf-fail2ban-stack.git
cd nginx-nginxui-waf-fail2ban-stack

sudo cp fail2ban/jail.local /etc/fail2ban/jail.local
sudo cp fail2ban/filter.d/openappsec.conf /etc/fail2ban/filter.d/

sudo systemctl restart fail2ban
