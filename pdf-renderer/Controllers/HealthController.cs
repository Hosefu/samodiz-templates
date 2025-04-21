using Microsoft.AspNetCore.Mvc;

namespace PdfRenderer.Controllers
{
    [ApiController]
    [Route("api/health")]
    public class HealthController : ControllerBase
    {
        [HttpGet]
        public IActionResult HealthCheck()
        {
            return Ok(new { status = "ok" });
        }
    }
} 