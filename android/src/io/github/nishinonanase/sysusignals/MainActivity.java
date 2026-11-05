package io.github.nishinonanase.sysusignals;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.webkit.*;
import android.widget.Toast;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public final class MainActivity extends Activity {
 private WebView web;
 private ValueCallback<Uri[]> chooser;
 private byte[] pendingExport;
 private static final int EXPORT=41, IMPORT=42;
 private static final String HOST="appassets.androidplatform.net";
 private static final String PUBLIC="https://nishino0525nanase.github.io/sysu-signals-study/";
 @Override public void onCreate(Bundle saved) {
  super.onCreate(saved);
  getWindow().setStatusBarColor(Color.rgb(25,59,56));
  getWindow().setNavigationBarColor(Color.rgb(245,246,242));
  web=new WebView(this);setContentView(web);
  WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
  settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  settings.setTextZoom(100);web.setBackgroundColor(Color.rgb(245,246,242));
  web.addJavascriptInterface(new BackupBridge(),"Android");
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
    Uri uri=request.getUrl();if(!"https".equals(uri.getScheme())||!HOST.equals(uri.getHost()))return blocked();
    String path=uri.getPath();if(path==null||!path.startsWith("/assets/")||path.contains(".."))return blocked();
    String asset=path.substring(8);try{return new WebResourceResponse(mime(asset),"UTF-8",getAssets().open(asset));}catch(IOException e){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",null,new ByteArrayInputStream("File not found".getBytes(StandardCharsets.UTF_8)));}
   }
   @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){return navigate(request.getUrl());}
  });
  web.setWebChromeClient(new WebChromeClient(){
   @Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){
    if(chooser!=null)chooser.onReceiveValue(null);chooser=callback;
    try{Intent intent=params.createIntent();intent.addCategory(Intent.CATEGORY_OPENABLE);startActivityForResult(intent,IMPORT);return true;}catch(Exception ex){chooser.onReceiveValue(null);chooser=null;Toast.makeText(MainActivity.this,"未找到文件选择器",Toast.LENGTH_SHORT).show();return false;}
   }
  });
  web.setDownloadListener(new DownloadListener(){@Override public void onDownloadStart(String url,String userAgent,String contentDisposition,String mimetype,long contentLength){
   Uri uri=Uri.parse(url);if(HOST.equals(uri.getHost())){String p=uri.getPath();String relative=p!=null?p.replaceFirst("^/assets/www/",""):"";openExternal(Uri.parse(PUBLIC+relative));}else if(url.startsWith("https://"))openExternal(uri);
  }});
  web.loadUrl("https://"+HOST+"/assets/www/index.html?android=1");
 }
 private WebResourceResponse blocked(){return new WebResourceResponse("text/plain","UTF-8",403,"Forbidden",null,new ByteArrayInputStream(new byte[0]));}
 private static String mime(String name){String n=name.toLowerCase(Locale.ROOT);if(n.endsWith(".html"))return "text/html";if(n.endsWith(".js"))return "application/javascript";if(n.endsWith(".css"))return "text/css";if(n.endsWith(".json")||n.endsWith(".webmanifest"))return "application/json";if(n.endsWith(".svg"))return "image/svg+xml";if(n.endsWith(".png"))return "image/png";if(n.endsWith(".webp"))return "image/webp";if(n.endsWith(".jpg"))return "image/jpeg";if(n.endsWith(".woff2"))return "font/woff2";if(n.endsWith(".woff"))return "font/woff";if(n.endsWith(".ttf"))return "font/ttf";if(n.endsWith(".pdf"))return "application/pdf";return "application/octet-stream";}
 private boolean navigate(Uri uri){if("https".equals(uri.getScheme())&&HOST.equals(uri.getHost()))return false;if("https".equals(uri.getScheme())||"http".equals(uri.getScheme()))openExternal(uri);return true;}
 private void openExternal(Uri uri){try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception e){Toast.makeText(this,"未找到浏览器",Toast.LENGTH_SHORT).show();}}
 private final class BackupBridge {
  @JavascriptInterface public void exportProgress(String json){if(json==null||json.length()>5000000)return;pendingExport=json.getBytes(StandardCharsets.UTF_8);runOnUiThread(new Runnable(){@Override public void run(){Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("application/json");intent.putExtra(Intent.EXTRA_TITLE,"信号研习室_学习记录.json");try{startActivityForResult(intent,EXPORT);}catch(Exception e){pendingExport=null;Toast.makeText(MainActivity.this,"未找到保存文件的位置",Toast.LENGTH_SHORT).show();}}});}
 }
 @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==IMPORT&&chooser!=null){chooser.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(result,data));chooser=null;}if(request==EXPORT){if(result==RESULT_OK&&data!=null&&data.getData()!=null&&pendingExport!=null){try(OutputStream out=getContentResolver().openOutputStream(data.getData())){if(out!=null)out.write(pendingExport);Toast.makeText(this,"学习记录已保存",Toast.LENGTH_SHORT).show();}catch(IOException e){Toast.makeText(this,"保存失败，请重试",Toast.LENGTH_SHORT).show();}}pendingExport=null;}}
 @Override public void onBackPressed(){web.evaluateJavascript("(function(){for(var id of ['image-dialog','reader']){var d=document.getElementById(id);if(d&&d.open){d.close();return true;}}return false;})()",new ValueCallback<String>(){@Override public void onReceiveValue(String closed){if(!"true".equals(closed)){if(web.canGoBack())web.goBack();else finish();}}});}
 @Override protected void onDestroy(){if(chooser!=null)chooser.onReceiveValue(null);web.removeJavascriptInterface("Android");web.destroy();super.onDestroy();}
}
