package config

import (
	"time"

	"github.com/spf13/viper"
)

// Config определяет конфигурацию для сервиса
type Config struct {
	Server          ServerConfig          `mapstructure:"server"`
	Renderers       RenderersConfig       `mapstructure:"renderers"`
	StorageAPI      StorageAPIConfig      `mapstructure:"storage_api"`
	TemplateAPI     TemplateAPIConfig     `mapstructure:"template_api"`
	TemplateService TemplateServiceConfig `mapstructure:"template_service"`
	HTTPClient      HTTPClientConfig      `mapstructure:"http_client"`
	LoggerConfig    LoggerConfig          `mapstructure:"logger"`
}

// ServerConfig определяет настройки HTTP сервера
type ServerConfig struct {
	Port            string        `mapstructure:"port"`
	ReadTimeout     time.Duration `mapstructure:"read_timeout"`
	WriteTimeout    time.Duration `mapstructure:"write_timeout"`
	ShutdownTimeout time.Duration `mapstructure:"shutdown_timeout"`
}

// RenderersConfig содержит URL различных сервисов-рендереров
type RenderersConfig struct {
	PDFRenderer string `mapstructure:"pdf_renderer"`
	PNGRenderer string `mapstructure:"png_renderer"`
}

// StorageAPIConfig содержит настройки для взаимодействия с сервисом хранения
type StorageAPIConfig struct {
	BaseURL string `mapstructure:"base_url"`
	APIKey  string `mapstructure:"api_key"`
}

// TemplateAPIConfig настройки для API шаблонов
type TemplateAPIConfig struct {
	BaseURL string `mapstructure:"base_url"`
	APIKey  string `mapstructure:"api_key"`
}

// TemplateServiceConfig настройки для сервиса шаблонизации
type TemplateServiceConfig struct {
	URL string `mapstructure:"url"`
}

// HTTPClientConfig настройки HTTP клиента
type HTTPClientConfig struct {
	Timeout         time.Duration `mapstructure:"timeout"`
	MaxIdleConns    int           `mapstructure:"max_idle_conns"`
	IdleConnTimeout time.Duration `mapstructure:"idle_conn_timeout"`
}

// LoggerConfig настройки логгера
type LoggerConfig struct {
	Level  string `mapstructure:"level"`
	Format string `mapstructure:"format"`
}

// LoadConfig загружает конфигурацию из файла и переменных окружения
func LoadConfig(path string) (*Config, error) {
	viper.SetConfigFile(path)
	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		return nil, err
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	// Установка значений по умолчанию
	setDefaults(&cfg)

	return &cfg, nil
}

// LoadConfigFromEnv загружает конфигурацию только из переменных окружения
func LoadConfigFromEnv() *Config {
	viper.AutomaticEnv()

	cfg := &Config{
		Server: ServerConfig{
			Port:            viper.GetString("SERVER_PORT"),
			ReadTimeout:     viper.GetDuration("SERVER_READ_TIMEOUT"),
			WriteTimeout:    viper.GetDuration("SERVER_WRITE_TIMEOUT"),
			ShutdownTimeout: viper.GetDuration("SERVER_SHUTDOWN_TIMEOUT"),
		},
		Renderers: RenderersConfig{
			PDFRenderer: viper.GetString("RENDERERS_PDF_RENDERER"),
			PNGRenderer: viper.GetString("RENDERERS_PNG_RENDERER"),
		},
		StorageAPI: StorageAPIConfig{
			BaseURL: viper.GetString("STORAGE_API_BASE_URL"),
			APIKey:  viper.GetString("STORAGE_API_KEY"),
		},
		TemplateAPI: TemplateAPIConfig{
			BaseURL: viper.GetString("TEMPLATE_API_BASE_URL"),
			APIKey:  viper.GetString("TEMPLATE_API_KEY"),
		},
		HTTPClient: HTTPClientConfig{
			Timeout:         viper.GetDuration("HTTP_CLIENT_TIMEOUT"),
			MaxIdleConns:    viper.GetInt("HTTP_CLIENT_MAX_IDLE_CONNS"),
			IdleConnTimeout: viper.GetDuration("HTTP_CLIENT_IDLE_CONN_TIMEOUT"),
		},
		LoggerConfig: LoggerConfig{
			Level:  viper.GetString("LOGGER_LEVEL"),
			Format: viper.GetString("LOGGER_FORMAT"),
		},
	}

	// Установка значений по умолчанию
	setDefaults(cfg)

	return cfg
}

// setDefaults устанавливает значения по умолчанию для конфигурации
func setDefaults(cfg *Config) {
	// Значения по умолчанию для сервера
	if cfg.Server.Port == "" {
		cfg.Server.Port = "8080"
	}
	if cfg.Server.ReadTimeout == 0 {
		cfg.Server.ReadTimeout = 10 * time.Second
	}
	if cfg.Server.WriteTimeout == 0 {
		cfg.Server.WriteTimeout = 30 * time.Second
	}
	if cfg.Server.ShutdownTimeout == 0 {
		cfg.Server.ShutdownTimeout = 5 * time.Second
	}

	// Значения по умолчанию для рендереров
	if cfg.Renderers.PDFRenderer == "" {
		cfg.Renderers.PDFRenderer = "http://pdf-renderer:8081/api/pdf/render"
	}
	if cfg.Renderers.PNGRenderer == "" {
		cfg.Renderers.PNGRenderer = "http://png-renderer:8082/api/png/render"
	}

	// Значения по умолчанию для сервиса шаблонизации
	if cfg.TemplateService.URL == "" {
		cfg.TemplateService.URL = "http://template-service:8083/api/template/render"
	}

	// Значения по умолчанию для API хранилища
	if cfg.StorageAPI.BaseURL == "" {
		cfg.StorageAPI.BaseURL = "http://storage-service:8000/api"
	}

	// Значения по умолчанию для HTTP клиента
	if cfg.HTTPClient.Timeout == 0 {
		cfg.HTTPClient.Timeout = 30 * time.Second
	}
	if cfg.HTTPClient.MaxIdleConns == 0 {
		cfg.HTTPClient.MaxIdleConns = 10
	}
	if cfg.HTTPClient.IdleConnTimeout == 0 {
		cfg.HTTPClient.IdleConnTimeout = 90 * time.Second
	}

	// Значения по умолчанию для логгера
	if cfg.LoggerConfig.Level == "" {
		cfg.LoggerConfig.Level = "info"
	}
	if cfg.LoggerConfig.Format == "" {
		cfg.LoggerConfig.Format = "json"
	}
}
