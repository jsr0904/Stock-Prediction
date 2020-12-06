package com.example.stock_prediction;

import android.os.Handler;
import android.os.Message;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

import java.util.Calendar;
import java.util.Timer;
import java.util.TimerTask;

public class RealActivity extends AppCompatActivity {
    Button disconnect;
    TextView tv,time;
    Calendar calendar;

    int port = 5006;
    int ex = 0;
    String ip = "192.168.145.136";

    private Socket clientSocket;
    private BufferedReader socketIn;
    private PrintWriter socketOut;
    private MyHandler2 myHandler;
    private MyThread2 myThread;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_real);

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        calendar = Calendar.getInstance();
        int year = calendar.get(Calendar.YEAR); // 년
        int month = calendar.get(Calendar.MONTH); // 월
        int day = calendar.get(Calendar.DAY_OF_MONTH); // 일
        int hour = calendar.get(Calendar.HOUR_OF_DAY); // 시
        int minute = calendar.get(Calendar.MINUTE); // 분
        int second = calendar.get(Calendar.SECOND); // 초

        time = (TextView) findViewById(R.id.R_time);
        time.setText(year + "년 " +
                (month+1) + "월 " + day + "일 " +
                hour + "시 " + minute + "분" +
                second + "초 \n"
        );

        tv = (TextView) findViewById(R.id.tv);
        tv.setMovementMethod(new ScrollingMovementMethod());
        tv.setText("Please Waiting for Prediction");

        try {
            clientSocket = new Socket(ip, port);
            socketIn = new BufferedReader(new InputStreamReader(clientSocket.getInputStream(), "UTF8"));
            socketOut = new PrintWriter(clientSocket.getOutputStream(), true);
        } catch (Exception e) {
            e.printStackTrace();
        }

        myHandler = new RealActivity.MyHandler2();
        myThread = new RealActivity.MyThread2();
        myThread.start();

        socketOut.println("real");
        tv.setText("");

    }

    public void onBackPressed() {
        finish();
        myThread.interrupt();
    }

    class MyThread2 extends Thread {
        @Override
        public void run() {
            while (true) {
                try {
                    // InputStream의 값을 읽어와서 data에 저장
                    String data = socketIn.readLine();
                    // Message 객체를 생성, 핸들러에 정보를 보낼 땐 이 메세지 객체를 이용
                    Message msg = myHandler.obtainMessage();
                    msg.obj = data;
                    myHandler.sendMessage(msg);
                    if(ex == 1) break;

                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }

    class MyHandler2 extends Handler {
        @Override
        public void handleMessage(Message msg) {
            //String result = msg.obj.toString();
            System.out.println(msg.obj);
            //System.out.println(result);
            if(msg.obj != null)
                tv.append(msg.obj+"\n");
        }
    }

}
