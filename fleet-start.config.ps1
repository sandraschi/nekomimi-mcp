# Per-repo fleet start config for nekomimi-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'nekomimi-mcp'
    BackendPort  = 11128
    FrontendPort = 11129
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind      = 'module-serve'
        Module    = 'nekomimi_mcp.server'
        ServeArgs = @('--http', '--port', '11128')
    }
    Frontend = @{
        Kind = 'vite-npm'
    }
}
