package com.example.navigation;

import android.bluetooth.BluetoothDevice;
import android.content.ClipData;
import android.content.Context;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.hivemq.client.mqtt.MqttClient;
import com.hivemq.client.mqtt.datatypes.MqttQos;
import com.hivemq.client.mqtt.exceptions.ConnectionClosedException;
import com.hivemq.client.mqtt.exceptions.ConnectionFailedException;
import com.hivemq.client.mqtt.exceptions.MqttClientStateException;
import com.hivemq.client.mqtt.exceptions.MqttEncodeException;
import com.hivemq.client.mqtt.exceptions.MqttSessionExpiredException;
import com.hivemq.client.mqtt.mqtt3.Mqtt3AsyncClient;
import com.hivemq.client.mqtt.mqtt3.Mqtt3BlockingClient;
import com.hivemq.client.mqtt.mqtt3.Mqtt3Client;
import com.hivemq.client.mqtt.mqtt3.exceptions.Mqtt3ConnAckException;
import com.hivemq.client.mqtt.mqtt3.message.connect.connack.Mqtt3ConnAck;
import com.hivemq.client.mqtt.mqtt3.message.publish.Mqtt3Publish;
import com.hivemq.client.mqtt.mqtt3.message.subscribe.suback.Mqtt3SubAck;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import android.content.ClipboardManager; // prefer this

import java.util.UUID;

public class AuthorizationFragment extends Fragment {
    TextView mDeviceidTv, mUrlTv, mPinTv, mAccountTv;
    Button mEnterBtn, mGeturlBtn, mAuthorizeBtn;

    String username = "androidapp";
    String password = "App49424D";
    boolean connected = false;
    boolean subscribed = false;
    String deviceid;
    String url = "";
    String pin = "";
    String account = "";

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View mView = inflater.inflate(R.layout.fragment_authorization, container, false);
        mDeviceidTv = mView.findViewById(R.id.deviceidTv);
        mUrlTv      = mView.findViewById(R.id.urlTv);
        mEnterBtn   = mView.findViewById(R.id.enterBtn);
        mGeturlBtn  = mView.findViewById(R.id.geturlBtn);
        mAuthorizeBtn  = mView.findViewById(R.id.authorizeBtn);
        mPinTv      = mView.findViewById(R.id.pinTv);
        mAccountTv  = mView.findViewById(R.id.accountTv);

        mAccountTv.setBackgroundColor(Color.argb(90,243, 202, 75));
        mUrlTv.setBackgroundColor(Color.argb(50,243, 202, 75));


        if(isNetworkConnected() == false){
            showToast("Please check the internet connection.");
        }

        Mqtt3AsyncClient client = MqttClient.builder()
                .useMqttVersion3()
                .identifier("androidapp")
                .serverHost("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud")
                .serverPort(8883)
                .sslWithDefaultConfig()
                .simpleAuth()
                    .username(username)
                    .password(password.getBytes())
                    .applySimpleAuth()
                .buildAsync();


        mEnterBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                deviceid = mDeviceidTv.getText().toString();
                if(deviceid.length() == 0){
                    showToast("Sorry, the content is null. Please type again.");
                    return;
                }else{
                    showToast("Received device id : " + deviceid);
                }

                while(connected == false){
                    MqttConnect(client);
                }
                String topic = "device" + deviceid;
                Log.i("androidapp", topic);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                String topic1 = topic + "/" + "url";
                String topic2 = topic + "/" + "account";
                MqttSubscribe(client, topic1, topic2);
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                MqttPublish(client, topic + "/" + "start", "hello");
           }
        });

        mGeturlBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(account.equals("google")){
                    mAccountTv.setText("Linking to Google account now...\nPlease go to the website https://www.google.com/device and enter the code below.");
                }else if(account.equals("twitter")){
                    mAccountTv.setText("Linking to Twitter account now...\nPlease go to the website shown below, complete the authorization process.\nThen enter the pin received in the response field below, and click AUTHORIZE.");
                }else if(account.equals("spotify")){
                    mAccountTv.setText("Linking to Spotify account now...\nPlease go to the website shown below, copy the link after jump.\nThen enter the pin received in the response field below, and click AUTHORIZE..");
                }
                if(url == ""){
                    showToast("something wrong happens, please try again later");
                }else{
                    mUrlTv.setText(url);
                }
            }
        });

//
//        mUrlTv.setOnClickListener(new View.OnClickListener() { // set onclick listener to my textview
//            @Override
//            public void onClick(View view) {
//                ClipboardManager cm = (ClipboardManager)getActivity().getApplicationContext().getSystemService(Context.CLIPBOARD_SERVICE);
//                ClipData clip = ClipData.newPlainText("url", mUrlTv.getText().toString());
//                cm.setPrimaryClip(clip);
//                showToast("url copied :)");
//            }
//        });

        mAuthorizeBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                pin = mPinTv.getText().toString();
                if(pin.length() == 0){
                    showToast("Sorry, the content is null. Please try again.");
                    return;
                }else{
                    showToast("Received!");
                }
                String topic = "device" + deviceid;
                MqttPublish(client, topic + "/pin", pin);
            }
        });

        return mView;
    }



    private void MqttConnect(Mqtt3AsyncClient client) {
        try{
            CompletableFuture<Mqtt3ConnAck> connAckFuture = client.connectWith()
                        .send()
                        .whenComplete((connAck, throwable) -> {
                            if (throwable != null) {
                                // Handle failure to publish
                                Log.i("androidapp", "failure publish after connect");
                            } else {
                                //
                            }
                    });
            connected = true;
        }catch(MqttClientStateException e){
            connected = true;
            Log.e("mqtterror","already connected");
        }catch(Mqtt3ConnAckException e){
            connected = false;
            Log.e("mqtterror","ConnAck message contained an error code");
        }catch(ConnectionClosedException e){
            connected = false;
            Log.e("mqtterror","the connection is closed after the Connect message has been sent but before a ConnAck message has been received");
        }catch (ConnectionFailedException e){
            connected = false;
            Log.e("mqtterror","an error occurs before the Connect message could be sent");
        }
    }

    private void MqttPublish(Mqtt3AsyncClient client, String topic, String msg){
        try{
            CompletableFuture<Mqtt3Publish> publishResultFuture = client.publishWith()
                    .topic(topic)
                    .payload(msg.getBytes())
                    .send()
                    .whenComplete((mqtt3Publish, throwable) -> {
                        if (throwable != null) {
                            // Handle failure to publish
                        } else {
                            // Handle successful publish, e.g. logging or incrementing a metric
                        }
                    });
            Log.i("androidapp", "publish success to " + topic);
        }catch(ConnectionClosedException e){
            Log.e("mqtterror", "for QoS 0 if the connection was closed during writing the message to the transport");
        }catch(MqttSessionExpiredException e){
            Log.e("mqtterror", "if the session expired before the message has been acknowledged completely");
        }catch(MqttEncodeException e){
            Log.e("mqtterror", "if the maximum packet size was exceeded");
        }catch(MqttClientStateException e){
            Log.e("mqtterror", "if the client is not connected and also not reconnecting");
        }

    }

    private void MqttSubscribe(Mqtt3AsyncClient client, String topic1, String topic2){
        //topic1 : url, topic2: account
        try {
            CompletableFuture<Mqtt3SubAck> subAckFuture =
                    client.subscribeWith()
//                            .topicFilter(topic)
                            .addSubscription().topicFilter(topic1).qos(MqttQos.AT_LEAST_ONCE).applySubscription()
                            .addSubscription().topicFilter(topic2).qos(MqttQos.AT_LEAST_ONCE).applySubscription()
                            .callback(publish -> {
                                String topic = publish.getTopic().toString();
                                Log.i("androidapp",topic);
                                Log.i("androidapp",new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8));
                                if (topic.equals(topic1)){
                                    url = new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8);
                                    Log.i("androidapp", url);
                                }
                                if(topic.equals(topic2)){
                                    account = new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8);
                                    Log.i("androidapp", account);
                                }
                            })
                            .send();
            subscribed = true;
        }catch(Exception e){
            e.printStackTrace();
            subscribed = false;
        }
    }

    //helper functions

    private void showToast(String msg) {
        Toast.makeText(getActivity(), msg, Toast.LENGTH_SHORT).show();

    }

    private boolean isNetworkConnected() {
        ConnectivityManager cm = (ConnectivityManager) getActivity().getSystemService(Context.CONNECTIVITY_SERVICE);
        return cm.getActiveNetworkInfo() != null && cm.getActiveNetworkInfo().isConnected();
    }
}