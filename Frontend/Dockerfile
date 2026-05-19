FROM nginx:alpine

# Copy the frontend file
COPY index.html /usr/share/nginx/html/index.template.html

# We use an entrypoint script to substitute the environment variable
# and then start Nginx
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-subst-backend-url.sh && \
    echo 'envsubst "\$BACKEND_URL" < /usr/share/nginx/html/index.template.html > /usr/share/nginx/html/index.html' >> /docker-entrypoint.d/40-subst-backend-url.sh && \
    chmod +x /docker-entrypoint.d/40-subst-backend-url.sh

# Default environment variable for local testing
ENV BACKEND_URL=http://localhost:8080

EXPOSE 80
