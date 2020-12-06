package com.example.stock_prediction;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.net.Uri;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.content.Intent;

class MyJavascriptInterface {

    @JavascriptInterface
    public void getHtml(String html) { //위 자바스크립트가 호출되면 여기로 html이 반환됨
        System.out.println(html);
    }
}

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        WebView webView = (WebView) findViewById(R.id.webView);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);

                view.loadUrl("javascript:window.Android.getHtml(document.getElementsByTagName('html')[0].innerHTML);"); //<html></html> 사이에 있는 모든 html을 넘겨준다.
            }
        });
        //
        webView.getSettings().setJavaScriptEnabled(true); //Javascript를 사용하도록 설정
        webView.addJavascriptInterface(new MyJavascriptInterface(), "Android");
        webView.loadUrl("https://m.stock.naver.com/");

        Button Prediction = (Button) findViewById(R.id.Prediction);
        Button Prediction2 = (Button) findViewById(R.id.Prediction2);
        Prediction.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v){
                Intent intent = new Intent(getApplicationContext()
                        ,predictActivity.class);
                startActivity(intent);
            }
        });
        Prediction2.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v){
                Intent intent = new Intent(getApplicationContext()
                        ,RealActivity.class);
                startActivity(intent);
            }
        });
    }
}
