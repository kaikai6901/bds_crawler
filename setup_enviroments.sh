sudo service tor stop
sudo service privoxy stop
sudo -u "debian-tor" screen -S tor -dm bash -c "tor -f /etc/tor/torrc"
sudo screen -S tor2 -dm bash -c "tor -f /etc/tor/torrc2"
sudo screen -S tor3 -dm bash -c "tor -f /etc/tor/torrc3"
sudo screen -S tor4 -dm bash -c "tor -f /etc/tor/torrc4"

sudo start-stop-daemon --start --exec /usr/sbin/privoxy --pidfile /var/run/privoxy.pid -- --user root /etc/privoxy/config
sudo start-stop-daemon --start --exec /usr/sbin/privoxy2 --pidfile /var/run/privoxy2.pid -- --user root /etc/privoxy2/config
sudo start-stop-daemon --start --exec /usr/sbin/privoxy3 --pidfile /var/run/privoxy3.pid -- --user root /etc/privoxy3/config
sudo start-stop-daemon --start --exec /usr/sbin/privoxy4 --pidfile /var/run/privoxy4.pid -- --user root /etc/privoxy4/config

