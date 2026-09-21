#include <stdio.h>

#ifdef _WIN32
// Код для компиляции под Windows
#include <windows.h>
int main() {
    Sleep(INFINITE); // Спим бесконечно, не потребляя ресурсов процессора
    return 0;
}
#else
// Код для компиляции под Linux / macOS
#include <unistd.h>
int main() {
    pause(); // Процесс засыпает до получения внешнего сигнала (например, SIGINT по Ctrl+C)
    return 0;
}
#endif