package com.example.stock_prediction;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;

public class StartActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_start);

        startLoading();
    }
    private void startLoading()       {
        Handler handler = new Handler();
        handler.postDelayed(new Runnable()       {
            public void run()
            {
                Intent s = new Intent(getApplicationContext()
                        , MainActivity.class);
                startActivity(s);
                finish();
            }
        },2000);

    }
}
