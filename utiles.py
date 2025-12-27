import psutil
import datetime
import os
import speedtest


# аптайм
def get_uptime():
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
    current_time = datetime.datetime.now()
    uptime = current_time - boot_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes


# CPU
def get_cpu_load():
    return psutil.cpu_percent(interval=1)


# RAM
def get_ram_load():
    ram_info = psutil.virtual_memory()
    return ram_info.percent


# Users
def get_active_users():
    active_users = os.popen('who').readlines()
    return len(active_users)


# Disk I/O
def get_disk_io():
    disk_io = psutil.disk_io_counters(perdisk=False)
    read_gb = round(disk_io.read_bytes / (1024 ** 3), 2)  # переводим в ГБ
    write_gb = round(disk_io.write_bytes / (1024 ** 3), 2)  # переводим в ГБ
    return read_gb, write_gb


# internet speed
def test_speed():
    try:

        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / 1_000_000, 2)  # преобразуем в Мбит/с и округляем
        upload_speed = round(st.upload() / 1_000_000, 2)  # преобразуем в Мбит/с и округляем
        ping = round(st.results.ping, 2)  # округляем

        # проверим что числовое значение #  Иногда speedtest возвращает ошибку
        if (isinstance(download_speed, (int, float)) and
                isinstance(upload_speed, (int, float)) and
                isinstance(ping, (int, float)) and
                download_speed > 0 and
                upload_speed > 0 and
                ping > 0):
            return download_speed, upload_speed, ping
        else:
            return 0, 0, 0

    except speedtest.ConfigRetrievalError:
        return 0, 0, 0
    except Exception:
        return 0, 0, 0