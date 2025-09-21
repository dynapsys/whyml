FROM php:8.2-apache

# Enable Apache modules
RUN a2enmod rewrite

# Set the working directory
WORKDIR /var/www/html

# Copy PHP configuration
COPY docker/php.conf /etc/apache2/sites-available/000-default.conf

# Create directory for PHP content
RUN mkdir -p /var/www/html

# Set permissions
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html

# Expose port 80
EXPOSE 80

# Start Apache
CMD ["apache2-foreground"]
