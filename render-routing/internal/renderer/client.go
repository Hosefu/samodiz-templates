package renderer

import (
	"context"
	"encoding/json"
	"fmt" // For reading response body

	// For debugging response content
	"strings" // For string operations

	"render-routing/internal/models"
	"render-routing/pkg/httputil"
	"render-routing/pkg/logger"
)

// Client представляет клиент для работы с рендерерами
type Client struct {
	pdfClient      *httputil.Client
	pngClient      *httputil.Client
	pdfRendererURL string
	pngRendererURL string
	logger         logger.Logger
}

// NewClient создает новый клиент для рендереров
func NewClient(pdfRendererURL, pngRendererURL string, httpConfig httputil.ClientConfig, logger logger.Logger) *Client {
	// Создаем клиенты для каждого рендерера
	pdfConfig := httpConfig
	pdfConfig.BaseURL = "" // URL передается полностью при запросе

	pngConfig := httpConfig
	pngConfig.BaseURL = "" // URL передается полностью при запросе

	return &Client{
		pdfClient:      httputil.NewClient(pdfConfig, logger),
		pngClient:      httputil.NewClient(pngConfig, logger),
		pdfRendererURL: pdfRendererURL,
		pngRendererURL: pngRendererURL,
		logger:         logger,
	}
}

// RenderPDF отправляет запрос на рендеринг PDF
func (c *Client) RenderPDF(ctx context.Context, request *models.PdfRendererRequest) (*models.RendererResponse, error) {
	c.logger.Infof("--- PDF RENDERING REQUEST START ---")
	c.logger.Infof("Sending PDF rendering request to %s with %d pages", c.pdfRendererURL, len(request.Pages))

	// Log the template ID and other request metadata
	c.logger.Infof("Template ID: %d, Generate Preview: %v", request.TemplateId, request.GeneratePreview)

	// Detailed logging for each page
	for i, page := range request.Pages {
		c.logger.Infof("Page %d: Dimensions %dx%d %s, HTML length: %d bytes",
			i+1, page.Width, page.Height, page.Units, len(page.HTML))

		// Log a preview of the HTML content
		if len(page.HTML) > 0 {
			htmlPreview := page.HTML
			if len(htmlPreview) > 200 {
				htmlPreview = htmlPreview[:200] + "..."
			}
			c.logger.Debugf("Page %d HTML preview: %s", i+1, htmlPreview)
		} else {
			c.logger.Warnf("Page %d has empty HTML content!", i+1)
		}

		// Log baseUri and settings
		c.logger.Infof("Page %d baseUri: %s", i+1, page.BaseUri)
		if len(page.Settings) > 0 {
			c.logger.Infof("Page %d settings: %+v", i+1, page.Settings)
		}
	}

	// Configure baseUri for each page
	for i, page := range request.Pages {
		// Always set a baseUri for assets access
		if page.BaseUri == "" {
			// URL for accessing resources through storage-service
			request.Pages[i].BaseUri = "http://storage-service:8000"
			c.logger.Infof("Set default baseUri for page %d: %s", i+1, request.Pages[i].BaseUri)
		}
	}

	// Handle assets information
	for i, page := range request.Pages {
		if page.Settings == nil {
			request.Pages[i].Settings = make(map[string]string)
		}

		// If assets exist, add them to settings for PDF renderer
		if len(page.Assets) > 0 {
			assetsJson, err := json.Marshal(page.Assets)
			if err == nil {
				request.Pages[i].Settings["assets"] = string(assetsJson)
				c.logger.Infof("Added %d assets to settings for page %d", len(page.Assets), i+1)

				// Log a few assets for debugging
				for j, asset := range page.Assets {
					if j < 3 { // Log only first 3 assets
						c.logger.Debugf("  Asset %d: %s", j+1, asset.File)
					}
				}
			} else {
				c.logger.Errorf("Failed to marshal assets: %v", err)
			}
		}
	}

	// Serialize the request to JSON for detailed logging
	requestData, err := json.MarshalIndent(request, "", "  ")
	if err != nil {
		c.logger.Errorf("Failed to marshal PDF request for logging: %v", err)
	} else {
		// Log a shortened version of the request JSON
		requestPreview := string(requestData)
		if len(requestPreview) > 1000 {
			lines := strings.Split(requestPreview, "\n")
			if len(lines) > 20 {
				requestPreview = strings.Join(lines[:20], "\n") + "\n... [truncated]"
			}
		}
		c.logger.Debugf("PDF render request JSON: %s", requestPreview)
	}

	// Create actual request data
	requestData, err = json.Marshal(request)
	if err != nil {
		c.logger.Errorf("Failed to marshal PDF request: %v", err)
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	c.logger.Infof("Sending request to PDF renderer (%d bytes)", len(requestData))

	// Отправляем запрос к PDF рендереру
	responseData, err := c.pdfClient.Post(ctx, c.pdfRendererURL, json.RawMessage(requestData), nil)
	if err != nil {
		c.logger.Errorf("Error sending request to PDF renderer: %v", err)
		return nil, fmt.Errorf("error sending request to PDF renderer: %w", err)
	}

	c.logger.Infof("Received response from PDF renderer: %d bytes", len(responseData))

	// Enhanced response validation - check if it looks like a PDF
	isPdf := isPdfContent(responseData)
	c.logger.Infof("Response validation - Looks like PDF: %v", isPdf)

	// If response is suspiciously small, log it for debugging
	if len(responseData) < 100 {
		// Log the small response content
		c.logger.Warnf("Suspiciously small response from PDF renderer: %d bytes", len(responseData))
		c.logger.Warnf("Response content: %s", string(responseData))

		// Try to parse as error JSON
		var errorResponse struct {
			Error   string `json:"error"`
			Message string `json:"message"`
		}

		if err := json.Unmarshal(responseData, &errorResponse); err == nil && errorResponse.Error != "" {
			c.logger.Errorf("PDF renderer returned error: %s - %s", errorResponse.Error, errorResponse.Message)
			return nil, fmt.Errorf("PDF renderer error: %s - %s", errorResponse.Error, errorResponse.Message)
		}

		// If not a valid JSON and too small, likely not a valid PDF
		if !isPdf {
			c.logger.Errorf("Response does not appear to be a valid PDF (too small: %d bytes)", len(responseData))
			return nil, fmt.Errorf("PDF renderer returned invalid data (size: %d bytes)", len(responseData))
		}
	}

	// Create the response
	var response models.RendererResponse

	// For PDF responses, we don't try to parse as JSON
	if isPdf {
		response.FileContent = responseData
	} else {
		// Try to parse as JSON response
		if err := json.Unmarshal(responseData, &response); err != nil {
			// If parsing fails, check if it might be binary data
			if len(responseData) > 100 {
				// Treat as binary PDF data
				c.logger.Infof("Response appears to be binary data, treating as PDF")
				response.FileContent = responseData
			} else {
				// Something went wrong
				c.logger.Errorf("Failed to parse response: %v", err)
				return nil, fmt.Errorf("invalid response from PDF renderer: %w", err)
			}
		} else if response.Error != "" {
			// If response contains error field
			c.logger.Errorf("PDF renderer reported error: %s", response.Error)
			return &response, nil
		}
	}

	// Final validation check
	if len(response.FileContent) < 50 {
		c.logger.Errorf("Final file content too small: %d bytes", len(response.FileContent))
		return nil, fmt.Errorf("renderer returned empty or invalid content (%d bytes)", len(response.FileContent))
	}

	c.logger.Infof("PDF rendering completed successfully, content size: %d bytes", len(response.FileContent))
	c.logger.Infof("--- PDF RENDERING REQUEST END ---")

	return &response, nil
}

// RenderPNG отправляет запрос на рендеринг PNG
func (c *Client) RenderPNG(ctx context.Context, request *models.RendererRequest) (*models.RendererResponse, error) {
	c.logger.Infof("--- PNG RENDERING REQUEST START ---")
	c.logger.Infof("Sending PNG rendering request to %s", c.pngRendererURL)

	// Log the request details
	c.logger.Infof("Page dimensions: %dx%d %s", request.Width, request.Height, request.Units)
	c.logger.Infof("HTML content length: %d bytes", len(request.HTML))

	// Log HTML preview
	if len(request.HTML) > 0 {
		htmlPreview := request.HTML
		if len(htmlPreview) > 200 {
			htmlPreview = htmlPreview[:200] + "..."
		}
		c.logger.Debugf("HTML preview: %s", htmlPreview)
	} else {
		c.logger.Warnf("HTML content is empty!")
	}

	// Log settings if present
	if len(request.Settings) > 0 {
		c.logger.Infof("PNG settings: %+v", request.Settings)
	}

	requestData, err := request.AsJSON()
	if err != nil {
		c.logger.Errorf("Failed to marshal PNG request: %v", err)
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	c.logger.Infof("Sending request to PNG renderer (%d bytes)", len(requestData))

	// Отправляем запрос к PNG рендереру
	responseData, err := c.pngClient.Post(ctx, c.pngRendererURL, json.RawMessage(requestData), nil)
	if err != nil {
		c.logger.Errorf("Error sending request to PNG renderer: %v", err)
		return nil, fmt.Errorf("error sending request to PNG renderer: %w", err)
	}

	c.logger.Infof("Received response from PNG renderer: %d bytes", len(responseData))

	// Enhanced validation - check if it looks like a PNG
	isPng := isPngContent(responseData)
	c.logger.Infof("Response validation - Looks like PNG: %v", isPng)

	// If response is suspiciously small, log it for debugging
	if len(responseData) < 100 {
		c.logger.Warnf("Suspiciously small response from PNG renderer: %d bytes", len(responseData))
		c.logger.Warnf("Response content: %s", string(responseData))

		// Try to parse as error JSON
		var errorResponse struct {
			Error string `json:"error"`
		}

		if err := json.Unmarshal(responseData, &errorResponse); err == nil && errorResponse.Error != "" {
			c.logger.Errorf("PNG renderer returned error: %s", errorResponse.Error)
			return nil, fmt.Errorf("PNG renderer error: %s", errorResponse.Error)
		}

		// If not a valid JSON and too small, likely not a valid PNG
		if !isPng {
			c.logger.Errorf("Response does not appear to be a valid PNG")
			return nil, fmt.Errorf("PNG renderer returned invalid data (size: %d bytes)", len(responseData))
		}
	}

	// Create the response
	var response models.RendererResponse

	// For PNG responses, we don't try to parse as JSON
	if isPng {
		response.FileContent = responseData
	} else {
		// Try to parse as JSON response
		if err := json.Unmarshal(responseData, &response); err != nil {
			// If parsing fails, check if it might be binary data
			if len(responseData) > 100 {
				// Treat as binary PNG data
				c.logger.Infof("Response appears to be binary data, treating as PNG")
				response.FileContent = responseData
			} else {
				// Something went wrong
				c.logger.Errorf("Failed to parse response: %v", err)
				return nil, fmt.Errorf("invalid response from PNG renderer: %w", err)
			}
		} else if response.Error != "" {
			// If response contains error field
			c.logger.Errorf("PNG renderer reported error: %s", response.Error)
			return &response, nil
		}
	}

	c.logger.Infof("PNG rendering completed successfully, content size: %d bytes", len(response.FileContent))
	c.logger.Infof("--- PNG RENDERING REQUEST END ---")

	return &response, nil
}

// Helper function to check if content looks like a PDF
func isPdfContent(data []byte) bool {
	// Check for PDF signature at the beginning (%PDF-)
	if len(data) >= 5 && string(data[:5]) == "%PDF-" {
		return true
	}
	return false
}

// Helper function to check if content looks like a PNG
func isPngContent(data []byte) bool {
	// Check for PNG signature at the beginning (89 50 4E 47 0D 0A 1A 0A)
	if len(data) >= 8 &&
		data[0] == 0x89 && data[1] == 0x50 && data[2] == 0x4E && data[3] == 0x47 &&
		data[4] == 0x0D && data[5] == 0x0A && data[6] == 0x1A && data[7] == 0x0A {
		return true
	}
	return false
}
