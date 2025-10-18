#!/usr/bin/env python3
"""Скрипт для проверки данных в базе данных."""

import asyncio
import asyncpg
from datetime import datetime


async def check_database():
    """Проверить данные в базе."""
    # Подключение к базе (используй свои данные)
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        database="systech_aidd",
        user="postgres",
        password="postgres"  # Измени на свой пароль
    )
    
    try:
        print("=" * 60)
        print("📊 ПРОВЕРКА БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        # Общее количество сообщений
        total = await conn.fetchval("SELECT COUNT(*) FROM messages")
        print(f"\n✅ Всего сообщений: {total}")
        
        # Активные (не удаленные) сообщения
        active = await conn.fetchval(
            "SELECT COUNT(*) FROM messages WHERE is_deleted = FALSE"
        )
        print(f"✅ Активных сообщений: {active}")
        
        # Последние 5 сообщений
        print("\n" + "=" * 60)
        print("📝 ПОСЛЕДНИЕ 5 СООБЩЕНИЙ:")
        print("=" * 60)
        
        rows = await conn.fetch(
            """
            SELECT id, user_id, username, role, 
                   LEFT(content, 50) as content_preview, 
                   created_at
            FROM messages
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        
        if rows:
            for row in rows:
                print(f"\nID: {row['id']}")
                print(f"  Пользователь: {row['username']} (ID: {row['user_id']})")
                print(f"  Роль: {row['role']}")
                print(f"  Текст: {row['content_preview']}...")
                print(f"  Дата: {row['created_at']}")
        else:
            print("\n⚠️ Нет сообщений в базе")
        
        # Статистика по пользователям
        print("\n" + "=" * 60)
        print("👥 СТАТИСТИКА ПО ПОЛЬЗОВАТЕЛЯМ:")
        print("=" * 60)
        
        users = await conn.fetch(
            """
            SELECT username, user_id, COUNT(*) as msg_count
            FROM messages
            WHERE is_deleted = FALSE
            GROUP BY username, user_id
            ORDER BY msg_count DESC
            LIMIT 10
            """
        )
        
        if users:
            for user in users:
                print(f"  {user['username']} (ID: {user['user_id']}): "
                      f"{user['msg_count']} сообщений")
        else:
            print("  Нет данных")
        
        print("\n" + "=" * 60)
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_database())



