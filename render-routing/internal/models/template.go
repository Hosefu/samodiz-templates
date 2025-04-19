package models

// Template представляет шаблон из storage-service
type Template struct {
	// ID шаблона
	ID int `json:"id"`

	// Имя шаблона
	Name string `json:"name"`

	// Версия шаблона
	Version string `json:"version"`

	// Тип шаблона (pdf, png, svg)
	Type string `json:"type"`

	// Страницы шаблона
	Pages []TemplatePage `json:"pages"`
}

// TemplatePage представляет страницу шаблона
type TemplatePage struct {
	// Имя страницы
	Name string `json:"name"`

	// HTML-содержимое страницы
	HTML string `json:"html"`

	// Ширина страницы
	Width int `json:"width"`

	// Высота страницы
	Height int `json:"height"`

	// Единицы измерения (px, mm)
	Units string `json:"units"`

	// Подрезы (bleed) для PDF
	Bleeds int `json:"bleeds,omitempty"`

	// Поля шаблона
	Fields []TemplateField `json:"fields"`

	// Ассеты страницы
	Assets []PageAsset `json:"assets"`

	// Дополнительные настройки
	Settings []PageSetting `json:"settings,omitempty"`
}

// TemplateField представляет поле шаблона
type TemplateField struct {
	// Имя поля
	Name string `json:"name"`

	// Метка поля
	Label string `json:"label,omitempty"`

	// Является ли поле обязательным
	Required bool `json:"required"`
}

// PageAsset представляет ассет страницы
type PageAsset struct {
	// URL файла
	File string `json:"file"`
}

// PageSetting представляет настройку страницы
type PageSetting struct {
	// Ключ настройки
	Key string `json:"key"`

	// Значение настройки
	Value string `json:"value"`
}

// GetField возвращает поле по имени
func (t *TemplatePage) GetField(name string) *TemplateField {
	for _, field := range t.Fields {
		if field.Name == name {
			return &field
		}
	}
	return nil
}

// GetSetting возвращает значение настройки по ключу
func (t *TemplatePage) GetSetting(key string) string {
	for _, setting := range t.Settings {
		if setting.Key == key {
			return setting.Value
		}
	}
	return ""
}

// GetSettingsMap возвращает настройки в виде map
func (t *TemplatePage) GetSettingsMap() map[string]string {
	settings := make(map[string]string)
	for _, setting := range t.Settings {
		settings[setting.Key] = setting.Value
	}
	return settings
}

// IsValid проверяет, что шаблон содержит хотя бы одну страницу
func (t *Template) IsValid() bool {
	return len(t.Pages) > 0
}
