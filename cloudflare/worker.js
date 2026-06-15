/**
 * Cloudflare Worker - D1 数据库 HTTP API 代理
 * 部署到 Cloudflare Workers 后，后端可以通过 HTTP API 访问 D1
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // 只允许 /api/d1/query 路径
    if (!url.pathname.startsWith('/api/d1/')) {
      return new Response(JSON.stringify({ error: 'Not Found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    try {
      if (request.method === 'POST' && url.pathname === '/api/d1/query') {
        const body = await request.json();
        const { sql, params } = body;
        
        if (!sql) {
          return new Response(JSON.stringify({ error: 'Missing SQL' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          });
        }

        // 执行查询
        const result = await env.DB.prepare(sql).bind(...(params || [])).all();
        
        return new Response(JSON.stringify({
          success: true,
          results: result.results,
        }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      if (request.method === 'GET' && url.pathname === '/api/d1/health') {
        // 健康检查
        await env.DB.prepare('SELECT 1').first();
        return new Response(JSON.stringify({ status: 'ok' }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (error) {
      return new Response(JSON.stringify({ 
        error: error.message,
        success: false,
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },
};
