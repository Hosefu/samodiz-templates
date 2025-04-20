package models

import (
	"encoding/json"
	"fmt"
)

// RenderRequest представляет запрос на рендеринг документа
type RenderRequest struct {
	// ID шаблона в storage-service
	TemplateID int `json:"template_id"`

	// Данные для подстановки в шаблон
	Data map[string]string `json:"data"`

	// Генерировать ли превью (для PDF)
	GeneratePreview bool `json:"generate_preview,omitempty"`
}

// Validate проверяет корректность запроса
func (r *RenderRequest) Validate() error {
	if r.TemplateID <= 0 {
		return fmt.Errorf("template_id must be positive")
	}

	if r.Data == nil {
		return fmt.Errorf("data field must not be null")
	}

	return nil
}

// RendererRequest представляет запрос к сервису рендеринга
type RendererRequest struct {
	// Обработанный HTML-контент шаблона с подставленными данными
	HTML string `json:"html"`

	// Данные для подстановки (требуется некоторым рендерерам)
	Data map[string]string `json:"data"`

	// Размеры страницы
	Width  int `json:"width"`
	Height int `json:"height"`

	// Единицы измерения (px, mm)
	Units string `json:"units"`

	// Подрезы (bleed) для PDF
	Bleeds int `json:"bleeds,omitempty"`

	// Генерировать ли превью (для PDF)
	GeneratePreview bool `json:"generate_preview,omitempty"`

	// Дополнительные настройки
	Settings map[string]string `json:"settings,omitempty"`
}

// StorageUploadRequest представляет запрос на загрузку файла в storage-service
type StorageUploadRequest struct {
	// ID шаблона
	TemplateID int `json:"template_id"`

	// Формат файла (pdf, png, svg)
	Format string `json:"format"`

	// Содержимое файла (бинарные данные)
	File []byte `json:"-"`

	// Данные, которые использовались при генерации
	FormData map[string]string `json:"form_data"`
}

// PdfRendererRequest представляет запрос к PDF-рендереру с поддержкой многостраничности
type PdfRendererRequest struct {
	// Массив страниц для рендеринга
	Pages []PdfPageRequest `json:"pages"`

	// Данные для подстановки (требуется некоторым рендерерам)
	Data map[string]string `json:"data"`

	// Генерировать ли превью
	GeneratePreview bool `json:"generate_preview,omitempty"`
}

// PdfPageRequest представляет данные одной страницы для PDF-рендерера
type PdfPageRequest struct {
	// HTML-контент страницы
	HTML string `json:"html"`

	// Размеры страницы
	Width  int `json:"width"`
	Height int `json:"height"`

	// Единицы измерения (px, mm)
	Units string `json:"units"`

	// Подрезы (bleed) для PDF
	Bleeds int `json:"bleeds"`

	// Дополнительные настройки
	Settings map[string]string `json:"settings,omitempty"`

	// Базовый URI для ресурсов (требуется PDF-рендерером)
	BaseUri string `json:"baseUri"`
}

// AsJSON сериализует объект в JSON
func (r *RenderRequest) AsJSON() ([]byte, error) {
	return json.Marshal(r)
}

// AsJSON сериализует объект в JSON
func (r *RendererRequest) AsJSON() ([]byte, error) {
	return json.Marshal(r)
}
