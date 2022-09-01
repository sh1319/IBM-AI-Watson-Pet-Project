package com.example.navigation;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.os.Bundle;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Set;
import java.util.UUID;

import pub.devrel.easypermissions.EasyPermissions;

public class BluetoothFragment extends Fragment {
    TextView mStatusBlueTv, mSsidTv, mPskTv, mReceivedMsgTv;
    ImageView mBlueIv;
    Button mOnBtn, mOffBtn, mRefreshBtn, mSendBtn;
    Spinner mSpinner;

    BluetoothAdapter mBlueAdapter;
    BluetoothSocket mSocket; //work as a client, a single BluetoothSocket to both initiate an outgoing connection and to manage the connection

    private BluetoothDeviceAdapter adapter_devices;

    final UUID uuid = UUID.fromString("643dddc4-5e4f-4072-ab90-6668d38c146d"); //UUID randomly generated
    final byte delimiter = 33; // character "!"
    int position = 0;

    private void RequiresPermission() {
        String[] perms = {Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT};
        if (EasyPermissions.hasPermissions(getContext(), perms)) {
        } else {
            // Do not have permissions, request them now
            EasyPermissions.requestPermissions(this, "bluetooth required", 100, perms);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View mView = inflater.inflate(R.layout.fragment_bluetooth, container, false);
        mStatusBlueTv  = mView.findViewById(R.id.statusBluetoothTv);
        mBlueIv        = mView.findViewById(R.id.bluetoothIv);
        mOnBtn         = mView.findViewById(R.id.onBth);
        mOffBtn        = mView.findViewById(R.id.offBth);
        mRefreshBtn    = mView.findViewById(R.id.refreshBtn);
        mSpinner       = mView.findViewById(R.id.devices_spinner);
        mSendBtn       = mView.findViewById(R.id.sendBtn);
        mSsidTv        = mView.findViewById(R.id.ssidTv);
        mPskTv         = mView.findViewById(R.id.pskTv);
        mReceivedMsgTv = mView.findViewById(R.id.receivedMsgTv);
        //adapter
        mBlueAdapter = BluetoothAdapter.getDefaultAdapter();

        //check if bluetooth is available or not
        if (mBlueAdapter == null) {
            mStatusBlueTv.setText("Bluetooth is not available");
        } else {
            mStatusBlueTv.setText("Bluetooth is available");
        }

        //set image according to bluetooth status (on/off)
        if (mBlueAdapter.isEnabled()) {
            mBlueIv.setImageResource(R.drawable.ic_action_on);
        } else {
            mBlueIv.setImageResource(R.drawable.ic_action_off);
        }

        ActivityResultLauncher<Intent> startBtActivityIntent = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult result) {
                        // Add same code that you want to add in onActivityResult method
                        if (result.getResultCode() == Activity.RESULT_OK) {
                            // bluetooth is on
                            mBlueIv.setImageResource(R.drawable.ic_action_on);
                            showToast("Bluetooth is on");
                        } else {
                            //user denied to turn bluetooth on
                            showToast("could not turn on bluetooth");
                        }
                    }
                });

        ActivityResultLauncher<Intent> startBtDsActivityIntent = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult result) {
                        if (result.getResultCode() == Activity.RESULT_CANCELED) {
                            //user denied to turn bluetooth discoverable
                            showToast("could not make bluetooth discoverable");
                        } else {
                            // bluetooth is discoverable
                            showToast("Bluetooth is discoverable");
                        }
                    }
                });

        //on btn click
        mOnBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!mBlueAdapter.isEnabled()) {
                    showToast("Turning on Bluetooth...");
                    //intent to on bluetooth
                    Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                    startBtActivityIntent.launch(intent);
                } else {
                    showToast("Bluetooth is already on");
                }

            }
        });

        //off btn click
        mOffBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                RequiresPermission();
                if (mBlueAdapter.isEnabled()) {
                    mBlueAdapter.disable();
                    showToast("Turning Bluetooth off");
                    mBlueIv.setImageResource(R.drawable.ic_action_off);
                } else {
                    showToast("Bluetooth is already off");
                }
            }
        });

        //refresh btn click
        mRefreshBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                BluetoothDeviceAdapter adapter_devices = new BluetoothDeviceAdapter(getActivity(), R.layout.bluetooth_devices_v1, new ArrayList<BluetoothDevice>());
                mSpinner.setAdapter(adapter_devices);

                BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

                if (!mBluetoothAdapter.isEnabled()) {
                    showToast("Turn on bluetooth to get paired devices");
                }

                Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
                if (pairedDevices.size() > 0) {
                    for (BluetoothDevice device : pairedDevices) {
                        adapter_devices.add(device);
                    }
                }

            }
        });

        //send btn click
        mSendBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String ssid = mSsidTv.getText().toString();
                String psk = mPskTv.getText().toString();
                BluetoothDevice device;
                if (mSpinner.getSelectedItem() == null){
                    showToast("Please choose the device paired.");
                    return;
                }else{
                    device = (BluetoothDevice) mSpinner.getSelectedItem();
                }
                Log.i("androidapp", String.valueOf(device.getBondState()));
                showToast("Successfully send! Pet starts network connecting process...");
                (new Thread(new BluetoothThread(ssid, psk, device))).start();
            }
        });


        return mView;
    }

    final class BluetoothThread implements Runnable {
        private String ssid;
        private String psk;
        private BluetoothDevice device;

        public BluetoothThread(String ssid, String psk, BluetoothDevice device) {
            this.ssid = ssid;
            this.psk = psk;
            this.device = device;
        }

        public void run() {
            clear();
            Log.i("androidapp", device.getName());

            try {
                //To create a BluetoothSocket for connecting to a known device, use BluetoothDevice.createRfcommSocketToServiceRecord()
                mSocket = device.createRfcommSocketToServiceRecord(uuid);
                if (!mSocket.isConnected()) {
                    mSocket.connect();
                    Thread.sleep(1000);
                }
                //open the IO streams by calling getInputStream() and getOutputStream() in order to retrieve InputStream and OutputStream objects, respectively
                // which are automatically connected to the socket.
                output("Bluetooth connection established.");

                OutputStream mOutputStream = mSocket.getOutputStream();
                final InputStream mInputStream = mSocket.getInputStream();

                waitForResponse(mInputStream);

                //send ssid
                mOutputStream.write(ssid.getBytes());
                mOutputStream.flush();
                waitForResponse(mInputStream);

                //send psk
                mOutputStream.write(psk.getBytes());
                mOutputStream.flush();
                waitForResponse(mInputStream);

                mSocket.close();

                output("Success.");

            } catch (Exception e) {
                output("Error: " + e.getMessage());
            }
        }
    }

    private void output(final String text) {
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                String currentText = mReceivedMsgTv.getText().toString();
                mReceivedMsgTv.setText(currentText + "\n" + text);
            }
        });
    }

    private void clear() {
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                mReceivedMsgTv.setText("");
            }
        });
    }

    private void waitForResponse(InputStream mInputStream) throws IOException {
        int bytesAvailable;

        while (true) {
            bytesAvailable = mInputStream.available();
            if (bytesAvailable > 0) {
                byte[] packetBytes = new byte[bytesAvailable];
                byte[] inputBuffer = new byte[1024];
                mInputStream.read(packetBytes); //Reads the next byte of data from the input stream.

                for (int i = 0; i < bytesAvailable; i++) {
                    byte b = packetBytes[i];

                    if (b == delimiter) {
                        byte[] msg = new byte[position]; //create bytes with space = content before delimiter
                        System.arraycopy(inputBuffer, 0, msg, 0, msg.length); //copy content from readBuffer to msg
                        final String msgReceived = new String(msg, "US-ASCII");

                        output("Received:" + msgReceived);

                        return;
                    } else {
                        inputBuffer[position++] = b;
                    }
                }
            }
        }
    }

    //toast message function
    private void showToast(String msg) {
        Toast.makeText(getActivity(), msg, Toast.LENGTH_SHORT).show();
    }
}