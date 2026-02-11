# antigravity_bot.py (Client)
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Stitch 서버 실행 파라미터 설정
    server_params = StdioServerParameters(
        command="python",
        args=["./stitch_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Stitch가 가진 도구 목록 확인
            await session.initialize()
            tools = await session.list_tools()
            
            # 2. 도구 사용 요청 (예: 브랜드 컬러 가져오기)
            result = await session.call_tool("get_brand_colors", arguments={"service_type": "bottle"})
            print(f"[Antigravity] Stitch에게 받은 컬러 정보: {result.content}")

if __name__ == "__main__":
    asyncio.run(run())