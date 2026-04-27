# ˵ģ

ĵʹͨʾκʵϢ

## ƼĿ¼ṹ

```text
/opt/sub-convert/
  app/
  venv/

/srv/sub-convert/subscriptions/
```

˵

- `/opt/sub-convert/app` Ŀ
- `/opt/sub-convert/venv`  Python ⻷
- `/srv/sub-convert/subscriptions` ԭʼ Base64 Դɽ

## 1. ϴĿ

Ѳֿݷŵ

```bash
/opt/sub-convert/app
```

## 2. ʹòű

Ƽֱʹã

```bash
cd /opt/sub-convert/app
bash deploy/bootstrap.sh
```

Ҳԣ

```bash
bash deploy/install.sh
```

## 3. bootstrap.sh ʲô

űԶɣ

- Ƿ root 
-  `/etc/os-release`
- ϵͳǷΪ Debian / Ubuntu
-  `apt-get`
-  `python3`
-  `systemctl`
- ĿĿ¼`requirements.txt`systemd ģ
- װ `python3``python3-venv``python3-pip``ca-certificates`
- ⻷
- װ Python 
- Ŀ¼뻺Ŀ¼
- װ systemd 
- ز

## 4. ĬĿ¼

űĬʹã

- `APP_DIR=/opt/sub-convert`
- `PROJECT_DIR=/opt/sub-convert/app`
- `VENV_DIR=/opt/sub-convert/venv`
- `SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions`

ҪԶ壬

```bash
APP_DIR=/data/sub-convert \
PROJECT_DIR=/data/sub-convert/app \
VENV_DIR=/data/sub-convert/venv \
SUBSCRIPTIONS_DIR=/data/subscriptions \
bash deploy/bootstrap.sh
```

## 5. ֶβ

```bash
cd /opt/sub-convert/app
PYTHONPATH=. /opt/sub-convert/venv/bin/python -m subscription_converter.cli --once
```

ɹʱῴƣ

```text
Processed sources: ['myhy2']
```

ɣ

```text
/srv/sub-convert/subscriptions/myhy2.yaml
/srv/sub-convert/subscriptions/myhy2.json
```

## 6. ״̬

```bash
systemctl status subscription-converter.service --no-pager
```

## 7. ĬΪ

Ĭû᣺

- ÿ `10` ɨһĿ¼
- ÿ `24` СʱˢһԶ̹

Ĭֵڣ

- `subscription_converter/config.py`

## 8. ֿ

ҪЩֱдֿ⣺

- ʵ
- ʵ IP
- ʵûĿ¼
- ˽Կtoken
- ˽·ʵάע

ʵʲʾ·ֻͬԼ˽л滻Ҫֱӻдֿ⡣
