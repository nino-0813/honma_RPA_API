from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import uuid
from datetime import datetime
import threading

app = FastAPI(title="RPA実行API")

# CORS設定（Reactアプリからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://localhost:5501",
    ],  # React開発サーバーとNext.jsのポート
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RPARequest(BaseModel):
    platform: str  # "base", "shopify", "rakuten", "furusato"
    user_id: Optional[str] = None  # ユーザーID（オプション）
    login_url: Optional[str] = None  # ログインページのURL（オプション、現在は未使用）
    orders_url: Optional[str] = None  # 注文一覧ページのURL（オプション、現在は未使用）


class RPAResponse(BaseModel):
    job_id: str
    platform: str
    status: str
    message: str


@app.get("/")
def read_root():
    return {"message": "RPA実行APIサーバー"}


@app.post("/run-rpa-simple")
async def run_rpa_simple(user_id: Optional[str] = None):
    """
    シンプルなRPA実行エンドポイント（パラメータ不要）
    新しい構造のRPAを使用
    """
    import threading
    from rpa.platforms.base_rpa import run_base_rpa
    
    job_id = str(uuid.uuid4())
    
    try:
        # バックグラウンドでRPAを実行（スレッドで実行）
        def run_rpa_thread():
            try:
                run_base_rpa(job_id=job_id, user_id=user_id)
            except Exception as e:
                print(f"[FastAPI] RPA実行エラー: {e}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=run_rpa_thread, daemon=True)
        thread.start()
        
        return {
            "status": "RPA started",
            "job_id": job_id,
            "message": "RPAが起動しました。ブラウザが開きますので、ログイン後、注文を取得します。"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RPA実行エラー: {str(e)}"
        )


@app.post("/run-rpa", response_model=RPAResponse)
async def run_rpa(request: RPARequest):
    """
    RPAスクリプトを実行するエンドポイント（プラットフォーム指定可能）
    新しい構造のRPAを使用
    """
    import threading
    
    platform = request.platform.lower()
    job_id = str(uuid.uuid4())
    
    # プラットフォームとRPA関数のマッピング
    platform_rpa_map = {
        "base": "rpa.platforms.base_rpa",
        "shopify": "rpa.platforms.shopify_rpa",
        "rakuten": "rpa.platforms.rakuten_rpa",
        "furusato": "rpa.platforms.furusato_rpa",
        "tabechoku": "rpa.platforms.tabechoku_rpa",
    }
    
    if platform not in platform_rpa_map:
        raise HTTPException(
            status_code=400,
            detail=f"サポートされていないプラットフォーム: {platform}"
        )
    
    try:
        # 動的にモジュールをインポート
        import importlib
        module_path = platform_rpa_map[platform]
        module = importlib.import_module(module_path)
        run_rpa_func = getattr(module, f"run_{platform}_rpa", None)
        
        if not run_rpa_func:
            raise HTTPException(
                status_code=500,
                detail=f"RPA関数が見つかりません: run_{platform}_rpa"
            )
        
        # バックグラウンドでRPAを実行（スレッドで実行）
        def run_rpa_thread():
            try:
                run_rpa_func(
                    job_id=job_id,
                    user_id=request.user_id
                )
            except Exception as e:
                print(f"[FastAPI] RPA実行エラー: {e}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=run_rpa_thread, daemon=True)
        thread.start()
        
        return RPAResponse(
            job_id=job_id,
            platform=platform,
            status="started",
            message=f"{platform.upper()} RPAが起動しました。ブラウザが開きますので、ログイン後、注文を取得します。"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RPA実行エラー: {str(e)}"
        )


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


class GenericRPARequest(BaseModel):
    login_url: str  # ログイン後のURL
    target_url: str  # データ取得対象のURL
    headless: Optional[bool] = False  # ヘッドレスモード
    user_id: Optional[str] = None  # ユーザーID（オプション）
    platform: Optional[str] = None  # プラットフォーム名（base, shopify, rakuten, furusato, tabechoku）


@app.post("/run-generic-rpa")
async def run_generic_rpa(request: GenericRPARequest):
    """
    汎用RPAを実行するエンドポイント
    
    Args:
        request: GenericRPARequest（login_url, target_url, headless, platform, user_id）
    
    Returns:
        Dict: 実行結果
    """
    try:
        from rpa.generic.main import run_generic_rpa as run_generic_rpa_func
    except ImportError as e:
        print(f"[FastAPI] モジュールインポートエラー: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"RPAモジュールのインポートに失敗しました: {str(e)}"
        )
    except Exception as e:
        print(f"[FastAPI] 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"予期しないエラーが発生しました: {str(e)}"
        )
    
    job_id = str(uuid.uuid4())
    
    # 結果を保持するための変数
    result_container = {"result": None, "error": None}
    
    try:
        # バックグラウンドでRPAを実行（スレッドで実行）
        def run_rpa_thread():
            try:
                print(f"[FastAPI] 汎用RPA実行を開始します (Job ID: {job_id})")
                print(f"[FastAPI] Login URL: {request.login_url}")
                print(f"[FastAPI] Target URL: {request.target_url}")
                print(f"[FastAPI] Platform: {request.platform}")
                
                result = run_generic_rpa_func(
                    login_url=request.login_url,
                    target_url=request.target_url,
                    headless=request.headless if request.headless is not None else False,
                    platform=request.platform,
                    user_id=request.user_id,
                    job_id=job_id
                )
                result_container["result"] = result
                print(f"[FastAPI] 汎用RPA実行が完了しました: {result}")
            except Exception as e:
                error_msg = f"エラーが発生しました: {str(e)}"
                print(f"[FastAPI] 汎用RPA実行エラー: {e}")
                import traceback
                traceback.print_exc()
                result_container["result"] = {
                    "success": False,
                    "saved_records": {"customers": 0, "orders": 0, "items": 0},
                    "message": error_msg
                }
                result_container["error"] = str(e)
        
        thread = threading.Thread(target=run_rpa_thread, daemon=True)
        thread.start()
        
        # スレッドが完了するまで待機（最大5分）
        thread.join(timeout=300)
        
        # 結果を取得
        if result_container["error"]:
            # エラーが発生した場合
            raise HTTPException(
                status_code=500,
                detail=f"RPA実行中にエラーが発生しました: {result_container['error']}"
            )
        
        if result_container["result"]:
            result = result_container["result"]
            if result.get("success"):
                return {
                    "status": "success",
                    "job_id": job_id,
                    "message": result.get("message", "RPA実行が完了しました"),
                    "saved_records": result.get("saved_records", {"customers": 0, "orders": 0, "items": 0})
                }
            else:
                # エラーが発生したが、結果は返された
                return {
                    "status": "error",
                    "job_id": job_id,
                    "message": result.get("message", "RPA実行中にエラーが発生しました"),
                    "saved_records": result.get("saved_records", {"customers": 0, "orders": 0, "items": 0})
                }
        else:
            # タイムアウトまたはまだ実行中
            return {
                "status": "started",
                "job_id": job_id,
                "message": f"汎用RPAが起動しました。ターゲットURL ({request.target_url}) からデータを取得します。"
            }
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        print(f"[FastAPI] 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"汎用RPA実行エラー: {str(e)}"
        )

