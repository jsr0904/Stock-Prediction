package com.example.stock_prediction;

import android.os.Handler;
import android.os.Message;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.Toast;


public class predictActivity extends AppCompatActivity {
    Button btn,disconnect;
    TextView tv,Sub;
    EditText text,value;

    int port = 5006;
    int ex = 0;
    String ip = "192.168.145.136";

    private Socket clientSocket;
    private BufferedReader socketIn;
    private PrintWriter socketOut;
    private MyHandler myHandler;
    private MyThread myThread;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_predict);

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        try {
            clientSocket = new Socket(ip, port);
            socketIn = new BufferedReader(new InputStreamReader(clientSocket.getInputStream(),"UTF8"));
            socketOut = new PrintWriter(clientSocket.getOutputStream(),true);
        } catch (Exception e) {
            e.printStackTrace();
        }

        myHandler = new MyHandler();
        myThread = new MyThread();
        myThread.start();

        text = (EditText) findViewById(R.id.insert);
        value = (EditText) findViewById(R.id.stock);
        btn = (Button) findViewById(R.id.btn);
        tv = (TextView) findViewById(R.id.tv);
        tv.setText("");
        disconnect = (Button) findViewById(R.id.disconnect);
        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(text.getText().length() == 0 || value.getText().length() == 0) {
                    Toast.makeText(getApplicationContext(), "TEXT와 주가%를 입력해주세요", Toast.LENGTH_LONG).show();
                    return;
                }

                socketOut.println(text.getText()+"/"+value.getText());
                text.setText("");
                value.setText("");

            }
        });
        disconnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                socketOut.println("exit");
                try {
                    clientSocket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                ex = 1;
                myThread.interrupt();
                finish();
            }
        });

    }

    public void onBackPressed() {
        socketOut.println("exit");
        try {
            clientSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        ex = 1;
        myThread.interrupt();
        finish();
    }

    class MyThread extends Thread {
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

    class MyHandler extends Handler {
        @Override
        public void handleMessage(Message msg) {
            String result = msg.obj.toString();
            tv.append(result+"\n");
        }
    }

}
