
## Installing via Docker

1. Download source

    ```
    git clone https://github.com/hechi/rooftop.git
    ```

2. Configure rooftop

  Important, change **AUTH_LDAP_\*** entries in **rooftop/settings.py**.
  You can store the ldap passwort into settings.py or into a single file called
  *ldap_passwd.txt*

  Generate secret key for django and save it into **secret_key.txt**
  You can use this command
  ```
  </dev/urandom tr -dc '12345!@#$%qwertQWERTasdfgASDFGzxcvbZXCVB' | head -c8; echo "" > secret_key.txt
  ```


3. Build docker image

    ```
    docker build -t rooftop ./
    ```

4. Run docker image

  docker runs in foreground
    ```
    docker run -v <path to repository>/rooftop/rooftop:/var/opt/rooftop/rooftop/ -p 80:80 -i rooftop
    ```

  docker runs in background
    ```
    docker run -d -v <path to repository>/rooftop/rooftop:/var/opt/rooftop/rooftop/ -p 80:80 -i rooftop
    ```
