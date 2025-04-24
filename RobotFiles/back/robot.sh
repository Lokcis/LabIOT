#!/bin/bash

set -e  # Detiene la ejecución si hay un error

LOG_FILE="$HOME/robot_monitor.log"

ROBOT_IP2="172.16.125.134"
STATUS_ROBOT2="OFFLINE"

FLOW_URL="https://prod-68.westus.logic.azure.com/workflows/822257e8e1e448af88d58d6869b273e5/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ofZLF_mLLAzFgCEL24rX83v2DCAZiacZqCFZlhetQLA"

send_teams_message() {
    local JSON_DATA="{
        \"robot_name\": \"$1\",
        \"robot_ip\": \"$2\",
        \"status\": \"$3\",
        \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S')\",
        \"voltage\": \"$4\",
        \"power_source\": \"$5\",
        \"port_in1\": \"$6\",
        \"port_in2\": \"$7\",
        \"port_in3\": \"$8\",
        \"port_in4\": \"$9\",
        \"port_outa\": \"${10}\",
        \"port_outb\": \"${11}\",
        \"port_outc\": \"${12}\",
        \"port_outd\": \"${13}\"
    }"

    echo "$(date '+%Y-%m-%d %H:%M:%S') - JSON enviado: $JSON_DATA" >> "$LOG_FILE"
    RESPONSE=$(curl --max-time 10 -s -w "\nCódigo de respuesta: %{http_code}\n" -X POST -H "Content-Type: application/json" -d "$JSON_DATA" "$FLOW_URL")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Respuesta: $RESPONSE" >> "$LOG_FILE"
}

get_robot_status_info() {
    local IP=$1
    ssh robot@"$IP" bash << 'EOF'
VOLTAGE="N/A"
if [ -e /sys/class/power_supply/lego-ev3-battery/voltage_now ]; then
    VOLTAGE_RAW=$(cat /sys/class/power_supply/lego-ev3-battery/voltage_now)
    VOLTAGE=$(awk "BEGIN {printf \"%.2f\", $VOLTAGE_RAW / 1000000}")
fi

POWER_SOURCE="Unknown"
if [ -e /sys/class/power_supply/lego-ev3-battery/technology ]; then
    RAW_SOURCE=$(cat /sys/class/power_supply/lego-ev3-battery/technology)
    POWER_SOURCE=$([ "$RAW_SOURCE" = "1" ] && echo "Battery" || echo "AC Adapter")
fi

PORT_IN1="Not connected"; PORT_IN2="Not connected"; PORT_IN3="Not connected"; PORT_IN4="Not connected"
PORT_OUTA="Not connected"; PORT_OUTB="Not connected"; PORT_OUTC="Not connected"; PORT_OUTD="Not connected"

for s in /sys/class/lego-sensor/sensor*; do
    [ -e "$s" ] || continue
    DRIVER=$(cat "$s/driver_name" 2>/dev/null)
    PATH_REAL=$(readlink -f "$s")
    case "$PATH_REAL" in
        *in1*) PORT_IN1="$DRIVER" ;;
        *in2*) PORT_IN2="$DRIVER" ;;
        *in3*) PORT_IN3="$DRIVER" ;;
        *in4*) PORT_IN4="$DRIVER" ;;
    esac
done

for m in /sys/class/tacho-motor/motor*; do
    [ -e "$m" ] || continue
    DRIVER=$(cat "$m/driver_name" 2>/dev/null)
    PATH_REAL=$(readlink -f "$m")
    case "$PATH_REAL" in
        *outA*) PORT_OUTA="$DRIVER" ;;
        *outB*) PORT_OUTB="$DRIVER" ;;
        *outC*) PORT_OUTC="$DRIVER" ;;
        *outD*) PORT_OUTD="$DRIVER" ;;
    esac
done

echo "$VOLTAGE|$POWER_SOURCE|$PORT_IN1|$PORT_IN2|$PORT_IN3|$PORT_IN4|$PORT_OUTA|$PORT_OUTB|$PORT_OUTC|$PORT_OUTD"
EOF
}

check_robot() {
    local IP=$1
    local NAME=$2
    local STATUS_VAR_NAME=$3

    if ping -c 1 -W 1 "$IP" > /dev/null 2>&1; then
        NEW_STATUS="ONLINE"
    else
        NEW_STATUS="OFFLINE"
    fi

    eval "OLD_STATUS=\$$STATUS_VAR_NAME"

    if [ "$NEW_STATUS" != "$OLD_STATUS" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $NAME ($IP) cambió a $NEW_STATUS" >> "$LOG_FILE"

        if [ "$NEW_STATUS" == "ONLINE" ]; then
            ROBOT_INFO=$(get_robot_status_info "$IP")
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Datos recibidos de $NAME: $ROBOT_INFO" >> "$LOG_FILE"
            IFS='|' read -r VOLTAGE POWER_SOURCE PORT_IN1 PORT_IN2 PORT_IN3 PORT_IN4 PORT_OUTA PORT_OUTB PORT_OUTC PORT_OUTD <<< "$ROBOT_INFO"
        else
            VOLTAGE="N/A"; POWER_SOURCE="N/A"
            PORT_IN1="N/A"; PORT_IN2="N/A"; PORT_IN3="N/A"; PORT_IN4="N/A"
            PORT_OUTA="N/A"; PORT_OUTB="N/A"; PORT_OUTC="N/A"; PORT_OUTD="N/A"
        fi

        send_teams_message "$NAME" "$IP" "$NEW_STATUS" "$VOLTAGE" "$POWER_SOURCE" "$PORT_IN1" "$PORT_IN2" "$PORT_IN3" "$PORT_IN4" "$PORT_OUTA" "$PORT_OUTB" "$PORT_OUTC" "$PORT_OUTD"
        eval "$STATUS_VAR_NAME=\"$NEW_STATUS\""
    fi
}

while true; do
    check_robot "$ROBOT_IP2" "Robot 2" "STATUS_ROBOT2"
    echo "--------------------------------" >> "$LOG_FILE"

    if [ "$STATUS_ROBOT2" = "OFFLINE" ]; then
        sleep 5
    else
        sleep 300
    fi
done
