FROM nginx:alpine

LABEL author="Simon Richardson"
#VOLUME /var/cache/nginx
#instead of using volume to map to local directory
COPY ./www /data/www

# Copy custom nginx config
COPY ./config/nginx.conf /etc/nginx/nginx.conf

# Copy self-signing cert: https://devcenter.heroku.com/articles/ssl-certificate-self
COPY ./certs/server.crt    /etc/nginx/server.crt
COPY ./certs/server.key    /etc/nginx/server.key

# Copy DHE handshake and dhparam https://bjornjohansen.no/optimizing-https-nginx
COPY ./certs/dhparam.pem   /etc/nginx/dhparam.pem

# Make cert key only available to owner (root)
RUN chmod 600 /etc/nginx/server.key

EXPOSE 80 443

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

# To build:
# docker build --tag richarsi/richarsi.website .
#
# To run: 
# docker run -d -p 8080:80 --name nginx richarsi/richarsi.website
#
# The website can then be accessed from your browser on localhost port 8000
# http://localhost:8080/
