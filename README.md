# 🤖 Myzoon Monitor Bot

Телеграм-бот для мониторинга инфраструктуры: TimeWeb Cloud, PolzaAI, Яндекс Вебмастер.

## Возможности

- 💰 Балансы TimeWeb Cloud и PolzaAI
- ⏳ Прогноз, когда закончится баланс TimeWeb (по дневным списаниям)
- 📦 Сводка по продуктам TimeWeb и ориентировочным расходам
- 📊 Метрики использования API-ключей PolzaAI (запросы, токены, расход, fallback по endpoint'ам)
- 🖥️ Статус VPS-серверов (CPU, RAM, диск, IP)
- 🔄 Управление серверами (мягкая/жёсткая перезагрузка, включение и выключение)
- 🌐 Список доменов
- 📈 Индексация и топ поисковых запросов (Яндекс)
- ⚠️ Авто-уведомления при низком балансе
- 🔴 Алерты при падении сервера
- 📊 Ежедневный сводный отчёт

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Главное меню с кнопками |
| `/status` | Статус серверов |
| `/balance` | Балансы всех сервисов |
| `/report` | Полный сводный отчёт |

## Мониторинг баланса PolzaAI

Да, мониторинг баланса уже есть в коде и запускается по расписанию в `scheduler.py`:
- бот запрашивает `https://polza.ai/api/v1/balance` (с fallback на альтернативный хост),
- сравнивает баланс с порогом `POLZAAI_BALANCE_THRESHOLD`,
- отправляет alert в `ADMIN_CHAT_ID`, если баланс ниже порога.

Интервал проверки задаётся `CHECK_INTERVAL` (в минутах).
Если нужна проверка раз в час как в примере, установите `CHECK_INTERVAL=60` в `.env`.


## Управление серверами

В карточке конкретного сервера доступны действия:
- ♻️ **Мягкая перезагрузка** (graceful reboot)
- 🔄 **Жёсткая перезагрузка**
- 🟢 **Включение**
- 🔴 **Выключение**

Если API TimeWeb не принимает конкретное имя действия, бот автоматически пробует альтернативные варианты (`soft_reboot` / `reboot_soft`, `start` / `power_on`, `shutdown` / `stop`).

---

## Установка на VPS TimeWeb

### 1. Подключитесь к серверу
```bash
ssh root@ВАШ_IP
```

### 2. Установите Python и зависимости
```bash
apt update && apt install python3 python3-venv python3-pip -y
```

### 3. Загрузите бота
```bash
git clone https://github.com/ВАШ_ЛОГИН/myzoon_bot.git /root/myzoon_bot
cd /root/myzoon_bot
```

### 4. Создайте виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Настройте переменные окружения
```bash
cp .env.example .env
nano .env
```

Заполните все значения в `.env` (см. раздел «Получение токенов»).

### 6. Запустите как сервис (автозапуск)
```bash
cp myzoon_bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable myzoon_bot
systemctl start myzoon_bot
```

### 7. Проверьте статус
```bash
systemctl status myzoon_bot
journalctl -u myzoon_bot -f  # логи в реальном времени
```

---

## Получение токенов

### Telegram Bot Token
1. Напишите [@BotFather](https://t.me/BotFather)
2. `/newbot` → задайте имя и username
3. Скопируйте токен в `BOT_TOKEN`

### Ваш Telegram User ID
Напишите [@userinfobot](https://t.me/userinfobot) — пришлёт ваш ID.

### TimeWeb Cloud API Token
1. Войдите в [панель TimeWeb](https://timeweb.cloud)
2. Аккаунт → API → Создать токен
3. Скопируйте в `TIMEWEB_API_TOKEN`

### PolzaAI API Key
Найдите в личном кабинете PolzaAI в разделе API / интеграции.

### Yandex Webmaster OAuth Token
1. Создайте приложение на [OAuth Яндекс](https://oauth.yandex.ru/)
2. Права: Яндекс.Вебмастер (чтение)
3. Получите токен
4. Ваш `YANDEX_USER_ID` — числовой ID аккаунта Яндекс
5. `YANDEX_HOST_ID` — формат `https:ваш-сайт.ru:443`

---

## Структура проекта

```
myzoon_bot/
├── bot.py                  # Точка входа
├── config.py               # Конфигурация
├── scheduler.py            # Планировщик (авто-уведомления)
├── formatters.py           # Форматирование сообщений
├── api/
│   ├── timeweb.py          # TimeWeb Cloud API
│   ├── polzaai.py          # PolzaAI API
│   └── yandex_webmaster.py # Яндекс Вебмастер API
├── handlers/
│   └── main.py             # Обработчики команд и кнопок
├── keyboards/
│   └── inline.py           # Inline-клавиатуры
├── requirements.txt
├── .env.example
└── myzoon_bot.service      # Systemd сервис
```
