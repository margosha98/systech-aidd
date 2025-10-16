# Команды для проверки БД во время тестирования

## Просмотр всех сообщений
```bash
docker exec systech-aidd-db psql -U postgres -d systech_aidd -c "SELECT id, user_id, role, LEFT(content, 50) as content_preview, content_length, is_deleted, created_at FROM messages ORDER BY created_at DESC LIMIT 10;"
```

## Статистика по сообщениям
```bash
docker exec systech-aidd-db psql -U postgres -d systech_aidd -c "SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE is_deleted = false) as active, COUNT(*) FILTER (WHERE is_deleted = true) as deleted, SUM(content_length) as total_chars FROM messages;"
```

## Просмотр по конкретному пользователю (замените YOUR_USER_ID)
```bash
docker exec systech-aidd-db psql -U postgres -d systech_aidd -c "SELECT role, content, content_length, is_deleted FROM messages WHERE user_id = YOUR_USER_ID ORDER BY created_at;"
```

## Очистка тестовых данных
```bash
docker exec systech-aidd-db psql -U postgres -d systech_aidd -c "TRUNCATE TABLE messages RESTART IDENTITY;"
```

