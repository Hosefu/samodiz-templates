using Microsoft.AspNetCore.Mvc;

namespace PdfRenderer.Controllers
{
    [ApiController]
    [Route("api/pdf")]
    public class HealthController : ControllerBase
    {
        [HttpGet("health/")]
        public IActionResult HealthCheck()
        {
            return Ok(new { status = "ok" });
        }
    }
} 