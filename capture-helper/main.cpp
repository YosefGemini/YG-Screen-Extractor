

#include <QCoreApplication>
#include <QDBusConnection>
#include <QDBusInterface>
#include <QDBusReply>
#include <QDBusUnixFileDescriptor>
#include <QDebug>
#include <QDir>
#include <QImage>
#include <QStringList>
#include <QVariantMap>

#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <unistd.h>
#include <vector>

namespace
{
    constexpr auto SERVICE = "org.kde.KWin.ScreenShot2";
    constexpr auto OBJECT_PATH = "/org/kde/KWin/ScreenShot2";
    constexpr auto INTERFACE = "org.kde.KWin.ScreenShot2";

    bool readAll(int fd, char *buffer, size_t size)
    {
        size_t total = 0;

        while (total < size)
        {
            const ssize_t count =
                ::read(fd, buffer + total, size - total);

            if (count < 0)
            {
                if (errno == EINTR)
                    continue;

                std::cerr << "Error leyendo la captura: "
                          << std::strerror(errno) << '\n';
                return false;
            }

            if (count == 0)
            {
                std::cerr
                    << "KWin cerró el pipe antes de completar la imagen.\n";
                return false;
            }

            total += static_cast<size_t>(count);
        }

        return true;
    }
}

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    const QStringList arguments = app.arguments();

    // Si se proporciona un nombre, captura ese monitor.
    // Si no se proporciona, conserva el modo de captura activa.
    const QString screenName =
        arguments.size() >= 2 ? arguments.at(1) : QString();

    // Crear el pipe que recibirá los píxeles enviados por KWin.
    int pipeFds[2];

    if (::pipe2(pipeFds, O_CLOEXEC) == -1)
    {
        std::cerr << "No se pudo crear el pipe: "
                  << std::strerror(errno) << '\n';
        return 1;
    }

    // Opciones de captura.
    QVariantMap options;
    options.insert(QStringLiteral("native-resolution"), true);
    options.insert(QStringLiteral("include-cursor"), false);

    QDBusInterface kwin(
        QString::fromLatin1(SERVICE),
        QString::fromLatin1(OBJECT_PATH),
        QString::fromLatin1(INTERFACE),
        QDBusConnection::sessionBus());

    if (!kwin.isValid())
    {
        std::cerr
            << "No se pudo conectar con la API de capturas de KWin.\n";

        ::close(pipeFds[0]);
        ::close(pipeFds[1]);
        return 2;
    }

    QDBusUnixFileDescriptor descriptor(pipeFds[1]);

    QDBusReply<QVariantMap> reply;

    if (screenName.isEmpty())
    {
        // Modo normal: capturar la pantalla activa de KWin.
        reply = kwin.call(
            QStringLiteral("CaptureActiveScreen"),
            options,
            QVariant::fromValue(descriptor));
    }
    else
    {
        // Modo rápido: capturar el monitor indicado.
        reply = kwin.call(
            QStringLiteral("CaptureScreen"),
            screenName,
            options,
            QVariant::fromValue(descriptor));
    }

    // Cerrar el descriptor de escritura original.
    // El descriptor enviado por D-Bus tiene su propia copia.
    ::close(pipeFds[1]);

    if (!reply.isValid())
    {
        std::cerr << "Error D-Bus: "
                  << reply.error().message().toStdString() << '\n';

        std::cerr << "Código: "
                  << reply.error().name().toStdString() << '\n';

        ::close(pipeFds[0]);
        return 3;
    }

    const QVariantMap metadata = reply.value();

    const int width =
        metadata.value(QStringLiteral("width")).toInt();

    const int height =
        metadata.value(QStringLiteral("height")).toInt();

    const int stride =
        metadata.value(QStringLiteral("stride")).toInt();

    const int formatValue =
        metadata.value(QStringLiteral("format")).toInt();

    const QString type =
        metadata.value(QStringLiteral("type")).toString();

    if (type != QStringLiteral("raw") ||
        width <= 0 ||
        height <= 0 ||
        stride <= 0)
    {
        std::cerr << "KWin devolvió metadatos de imagen inválidos.\n";
        ::close(pipeFds[0]);
        return 4;
    }

    // Validar el formato informado por KWin.
    const auto format = static_cast<QImage::Format>(formatValue);

    QImage formatCheck(1, 1, format);

    if (formatCheck.isNull())
    {
        std::cerr << "Formato de imagen no compatible con Qt: "
                  << formatValue << '\n';

        ::close(pipeFds[0]);
        return 5;
    }

    const size_t byteCount =
        static_cast<size_t>(stride) *
        static_cast<size_t>(height);

    // Evitar asignaciones excesivas ante metadatos incorrectos.
    constexpr size_t MAX_IMAGE_BYTES =
        512ULL * 1024ULL * 1024ULL;

    if (byteCount == 0 || byteCount > MAX_IMAGE_BYTES)
    {
        std::cerr << "Tamaño de captura inválido.\n";
        ::close(pipeFds[0]);
        return 6;
    }

    std::vector<char> pixels(byteCount);

    if (!readAll(pipeFds[0], pixels.data(), pixels.size()))
    {
        ::close(pipeFds[0]);
        return 7;
    }

    ::close(pipeFds[0]);

    QImage image(
        reinterpret_cast<const uchar *>(pixels.data()),
        width,
        height,
        stride,
        format);

    // Copiar los píxeles a memoria propiedad de QImage.
    image = image.copy();

    if (image.isNull())
    {
        std::cerr << "Qt no pudo construir la imagen capturada.\n";
        return 8;
    }

    const QString outputPath =
        QDir::homePath() + QStringLiteral("/capture.png");

    if (!image.save(outputPath, "PNG"))
    {
        std::cerr << "No se pudo guardar la imagen en: "
                  << outputPath.toStdString() << '\n';
        return 9;
    }

    std::cout << "Captura guardada en: "
              << outputPath.toStdString() << '\n';

    return 0;
}

