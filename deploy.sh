#!/bin/bash
# Script de despliegue

# Copia los archivos al sistema
sudo cp robot.sh /usr/local/bin/
sudo cp robot.service /etc/systemd/system/

# Recarga la configuración del sistema
sudo systemctl daemon-reload

# Otorga permisos de ejecución al script
sudo chmod +x /usr/local/bin/robot.sh

# Reinicia el servicio
sudo systemctl restart robot.service

echo "✅ Despliegue completado!"
