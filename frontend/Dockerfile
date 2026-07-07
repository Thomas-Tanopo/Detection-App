FROM nginx:alpine
RUN apk add --no-cache envsubst
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["/bin/sh", "/usr/share/nginx/html/start.sh"]