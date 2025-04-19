package models

import (
	"encoding/json"
	"time"
)

// RenderResponse представляет ответ API на запрос рендеринга
type RenderResponse struct {
	// URL сгенерированного файла
	URL string `json:"url"`

	// Формат файла (pdf, png, svg)
	Format string `json:"format"`

	// Время создания
	CreatedAt time.Time `json:"created_at"`

	// URL превью (для PDF)
	PreviewURL string `json:"preview_url,omitempty"`

	// Сообщение об ошибке (если есть)
	Error string `json:"error,omitempty"`
}

// RendererResponse представляет ответ от сервиса рендеринга
type RendererResponse struct {
	// Содержимое сгенерированного файла
	FileContent []byte `json:"-"`

	// URL превью (для PDF)
	PreviewURL string `json:"preview_url,omitempty"`

	// Сообщение об ошибке (если есть)
	Error string `json:"error,omitempty"`
}

// StorageUploadResponse представляет ответ от storage-service на загрузку файла
type StorageUploadResponse struct {
	// ID сгенерированного документа
	ID int `json:"id"`

	// URL сгенерированного файла
	URL string `json:"url"`

	// Время создания
	CreatedAt time.Time `json:"created_at"`

	// Формат файла (опционально)
	Format string `json:"format,omitempty"`
}

// ErrorResponse представляет ответ с ошибкой
type ErrorResponse struct {
	// Сообщение об ошибке
	Error string `json:"error"`

	// Код HTTP-ответа
	Code int `json:"code,omitempty"`
}

// FromJSON десериализует JSON в объект
func (r *RenderResponse) FromJSON(data []byte) error {
	return json.Unmarshal(data, r)
}

// FromJSON десериализует JSON в объект
func (r *StorageUploadResponse) FromJSON(data []byte) error {
	return json.Unmarshal(data, r)
}

// ToJSON сериализует объект в JSON
func (r *RenderResponse) ToJSON() ([]byte, error) {
	return json.Marshal(r)
}

// NewErrorResponse создает новый ответ с ошибкой
func NewErrorResponse(err string, code int) *ErrorResponse {
	return &ErrorResponse{
		Error: err,
		Code:  code,
	}
}
