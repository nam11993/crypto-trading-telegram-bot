"""
Script để lấy Telegram Chat ID
Chạy script này để lấy Chat ID của bạn
"""

import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

async def get_chat_id():
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ Lỗi: TELEGRAM_BOT_TOKEN chưa được cấu hình trong file .env")
        print("Hãy tạo bot với @BotFather và điền token vào .env")
        return
    
    try:
        bot = Bot(token=bot_token)
        
        print("🤖 Đang lấy thông tin chat...")
        print("📱 Hãy gửi tin nhắn '/start' cho bot của bạn trước!")
        
        # Get updates
        updates = await bot.get_updates()
        
        if not updates:
            print("⚠️  Không tìm thấy tin nhắn nào!")
            print("Hãy:")
            print("1. Tìm bot của bạn trên Telegram")
            print("2. Gửi tin nhắn '/start' cho bot")
            print("3. Chạy lại script này")
            return
        
        # Get chat information from updates
        print("\n📋 Danh sách Chat IDs tìm thấy:")
        print("-" * 40)
        
        chat_ids = set()
        for update in updates:
            if update.message:
                chat_id = update.message.chat.id
                chat_type = update.message.chat.type
                
                if chat_type == 'private':
                    first_name = update.message.chat.first_name or "Unknown"
                    username = update.message.chat.username or "No username"
                    print(f"👤 Private Chat: {first_name} (@{username})")
                    print(f"   Chat ID: {chat_id}")
                    chat_ids.add(chat_id)
                elif chat_type in ['group', 'supergroup']:
                    group_name = update.message.chat.title or "Unknown Group"
                    print(f"👥 Group: {group_name}")
                    print(f"   Chat ID: {chat_id}")
                    chat_ids.add(chat_id)
        
        if chat_ids:
            print(f"\n✅ Tìm thấy {len(chat_ids)} chat(s)")
            
            if len(chat_ids) == 1:
                selected_id = list(chat_ids)[0]
                print(f"\n🎯 Chat ID của bạn: {selected_id}")
                print(f"\nThêm dòng này vào file .env:")
                print(f"TELEGRAM_CHAT_ID={selected_id}")
            else:
                print(f"\n🎯 Các Chat IDs có sẵn:")
                for i, chat_id in enumerate(chat_ids, 1):
                    print(f"{i}. {chat_id}")
                print(f"\nChọn Chat ID phù hợp và thêm vào .env:")
                print(f"TELEGRAM_CHAT_ID=<your_selected_chat_id>")
        else:
            print("❌ Không tìm thấy chat nào!")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("Kiểm tra lại Bot Token trong file .env")

def main():
    print("🔍 Getting Telegram Chat ID...")
    print("=" * 40)
    
    try:
        asyncio.run(get_chat_id())
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng script")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()