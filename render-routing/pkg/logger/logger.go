package logger

import (
	"os"
	"strings"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// Logger определяет интерфейс для логирования
type Logger interface {
	Debug(msg string, fields ...interface{})
	Info(msg string, fields ...interface{})
	Warn(msg string, fields ...interface{})
	Error(msg string, fields ...interface{})
	Fatal(msg string, fields ...interface{})
	With(fields ...interface{}) Logger
	Debugf(template string, args ...interface{})
	Infof(template string, args ...interface{})
	Warnf(template string, args ...interface{})
	Errorf(template string, args ...interface{})
	Fatalf(template string, args ...interface{})
	WithField(key string, value interface{}) Logger
	WithFields(fields map[string]interface{}) Logger
}

// zapLogger реализует интерфейс Logger с использованием zap
type zapLogger struct {
	zap *zap.SugaredLogger
}

// New создает новый экземпляр логгера с заданным уровнем
func New(level, format string) Logger {
	// Преобразование строкового уровня в zapcore.Level
	var zapLevel zapcore.Level
	switch strings.ToLower(level) {
	case "debug":
		zapLevel = zapcore.DebugLevel
	case "info":
		zapLevel = zapcore.InfoLevel
	case "warn":
		zapLevel = zapcore.WarnLevel
	case "error":
		zapLevel = zapcore.ErrorLevel
	case "fatal":
		zapLevel = zapcore.FatalLevel
	default:
		zapLevel = zapcore.InfoLevel
	}

	// Конфигурация zap логгера
	config := zap.Config{
		Level:            zap.NewAtomicLevelAt(zapLevel),
		Development:      false,
		Encoding:         format,
		EncoderConfig:    zap.NewProductionEncoderConfig(),
		OutputPaths:      []string{"stdout"},
		ErrorOutputPaths: []string{"stderr"},
	}

	// Если формат не json или console, используем json по умолчанию
	if format != "json" && format != "console" {
		config.Encoding = "json"
	}

	// Настройка форматирования времени
	config.EncoderConfig.TimeKey = "timestamp"
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

	// Создание логгера
	baseLogger, err := config.Build()
	if err != nil {
		// В случае ошибки используем стандартную конфигурацию
		baseLogger = zap.NewExample().Sugar().Desugar()
	}
	defer baseLogger.Sync()

	sugar := baseLogger.Sugar()

	return &zapLogger{
		zap: sugar,
	}
}

// Debug логирует сообщение на уровне Debug
func (l *zapLogger) Debug(msg string, fields ...interface{}) {
	l.zap.Debugw(msg, fields...)
}

// Info логирует сообщение на уровне Info
func (l *zapLogger) Info(msg string, fields ...interface{}) {
	l.zap.Infow(msg, fields...)
}

// Warn логирует сообщение на уровне Warn
func (l *zapLogger) Warn(msg string, fields ...interface{}) {
	l.zap.Warnw(msg, fields...)
}

// Error логирует сообщение на уровне Error
func (l *zapLogger) Error(msg string, fields ...interface{}) {
	l.zap.Errorw(msg, fields...)
}

// Fatal логирует сообщение на уровне Fatal и завершает программу
func (l *zapLogger) Fatal(msg string, fields ...interface{}) {
	l.zap.Fatalw(msg, fields...)
}

// Debugf логирует форматированное сообщение с уровнем Debug
func (l *zapLogger) Debugf(template string, args ...interface{}) {
	l.zap.Debugf(template, args...)
}

// Infof логирует форматированное сообщение с уровнем Info
func (l *zapLogger) Infof(template string, args ...interface{}) {
	l.zap.Infof(template, args...)
}

// Warnf логирует форматированное сообщение с уровнем Warn
func (l *zapLogger) Warnf(template string, args ...interface{}) {
	l.zap.Warnf(template, args...)
}

// Errorf логирует форматированное сообщение с уровнем Error
func (l *zapLogger) Errorf(template string, args ...interface{}) {
	l.zap.Errorf(template, args...)
}

// Fatalf логирует форматированное сообщение с уровнем Fatal и выход
func (l *zapLogger) Fatalf(template string, args ...interface{}) {
	l.zap.Fatalf(template, args...)
	os.Exit(1)
}

// With добавляет поля к логгеру
func (l *zapLogger) With(fields ...interface{}) Logger {
	return &zapLogger{
		zap: l.zap.With(fields...),
	}
}

// WithField возвращает новый логгер с добавленным полем
func (l *zapLogger) WithField(key string, value interface{}) Logger {
	return &zapLogger{
		zap: l.zap.With(key, value),
	}
}

// WithFields возвращает новый логгер с добавленными полями
func (l *zapLogger) WithFields(fields map[string]interface{}) Logger {
	var args []interface{}
	for k, v := range fields {
		args = append(args, k, v)
	}
	return &zapLogger{
		zap: l.zap.With(args...),
	}
}
