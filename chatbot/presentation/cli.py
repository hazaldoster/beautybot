"""CLI Presentation Layer - interactive terminal chatbot interface."""

from __future__ import annotations
import sys
import os

from chatbot.application.services.chatbot_service import ChatbotService


# ANSI color codes
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


BANNER = f"""
{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          Trendyol BeautyBot - Güzellik Ürünleri Analiz Chatbot        ║
║                                                              ║
║   Trendyol güzellik ürünleri veritabanından anlamlı          ║
║   çıkarımlar yapan akıllı asistanınız.                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""

HELP_TEXT = f"""
{Colors.YELLOW}Komutlar:{Colors.RESET}
  {Colors.GREEN}/stats{Colors.RESET}    - Hızlı istatistikleri göster (LLM kullanmadan)
  {Colors.GREEN}/reset{Colors.RESET}    - Konuşmayı sıfırla
  {Colors.GREEN}/help{Colors.RESET}     - Bu yardım mesajını göster
  {Colors.GREEN}/quit{Colors.RESET}     - Chatbot'tan çık

{Colors.YELLOW}Örnek sorular:{Colors.RESET}
  - En çok yorum alan ürünler hangileri?
  - Kaş maskarası kategorisinde en iyi ürün hangisi?
  - En iyi fiyat/performans ürünlerini öner
  - Hangi ürünler tartışmalı yorumlara sahip?
  - Ruj kategorisinin genel analizi nedir?
  - Trend olan ürünler hangileri?
  - 100 TL altında iyi puanlı ürünler var mı?
"""


def run_cli(csv_path: str, api_key: str) -> None:
    """Run the interactive CLI chatbot."""
    print(BANNER)

    # Initialize chatbot
    print(f"{Colors.DIM}Veriler yükleniyor ve analiz ediliyor...{Colors.RESET}")

    try:
        chatbot = ChatbotService(csv_path=csv_path, gemini_api_key=api_key)
        status = chatbot.initialize()
        print(f"{Colors.GREEN}✓ {status}{Colors.RESET}")
        print(f"{Colors.DIM}Gemini LLM bağlamı hazırlandı.{Colors.RESET}")
    except FileNotFoundError as e:
        print(f"{Colors.RED}Hata: {e}{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Başlatma hatası: {e}{Colors.RESET}")
        sys.exit(1)

    print(HELP_TEXT)
    print(f"{Colors.CYAN}Merhaba! Ben Trendyol BeautyBot. Güzellik ürünleri hakkında her şeyi sorabilirsınız.{Colors.RESET}")
    print()

    # Main chat loop
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.BLUE}Sen > {Colors.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.DIM}Görüşmek üzere!{Colors.RESET}")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            command = user_input.lower()

            if command in ("/quit", "/exit", "/q"):
                print(f"{Colors.DIM}Görüşmek üzere! İyi günler dilerim.{Colors.RESET}")
                break

            elif command == "/help":
                print(HELP_TEXT)
                continue

            elif command == "/stats":
                try:
                    stats = chatbot.get_quick_stats()
                    print(f"\n{Colors.YELLOW}📊 Hızlı İstatistikler:{Colors.RESET}")
                    print(stats)
                    print()
                except Exception as e:
                    print(f"{Colors.RED}Hata: {e}{Colors.RESET}")
                continue

            elif command == "/reset":
                chatbot.reset_conversation()
                print(f"{Colors.GREEN}✓ Konuşma sıfırlandı.{Colors.RESET}\n")
                continue

            else:
                print(f"{Colors.RED}Bilinmeyen komut. /help yazarak komutları görebilirsiniz.{Colors.RESET}\n")
                continue

        # Send to LLM and stream response
        print(f"\n{Colors.BOLD}{Colors.CYAN}Trendyol BeautyBot > {Colors.RESET}", end="", flush=True)

        try:
            for chunk in chatbot.chat_stream(user_input):
                print(chunk, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"\n{Colors.RED}Yanıt alınırken hata oluştu: {e}{Colors.RESET}\n")


def main() -> None:
    """Entry point for the CLI chatbot."""
    # Determine CSV path
    csv_path = os.environ.get("BEAUTYBOT_CSV_PATH")
    if not csv_path:
        # Default: look for CSV in project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(project_root, "all_categories_20250207_031918.csv")

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"{Colors.RED}Hata: GEMINI_API_KEY ortam değişkeni ayarlanmamış.{Colors.RESET}")
        print(f"{Colors.DIM}Kullanım: GEMINI_API_KEY=your_key python -m chatbot{Colors.RESET}")
        sys.exit(1)

    run_cli(csv_path, api_key)


if __name__ == "__main__":
    main()
