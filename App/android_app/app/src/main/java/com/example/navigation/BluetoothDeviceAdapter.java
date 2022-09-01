package com.example.navigation;

import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.ArrayList;

public class BluetoothDeviceAdapter extends ArrayAdapter<BluetoothDevice> {

    private LayoutInflater inflater;
    private ArrayList<BluetoothDevice> devices;

    public BluetoothDeviceAdapter(Context context, int resource, ArrayList<BluetoothDevice> devices) {
        super(context, resource, devices);

        this.devices = devices;
        inflater = (LayoutInflater)context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    }

    @Override
    public BluetoothDevice getItem(int position) {
        return super.getItem(position);
    }

    @Override
    public View getDropDownView(int position, View convertView,ViewGroup parent) {
        View row = inflater.inflate(R.layout.bluetooth_devices_v1, parent, false);

        BluetoothDevice device = devices.get(position);

        TextView name = row.findViewById(R.id.name_label);
        TextView address = row.findViewById(R.id.address_label);

        name.setText(device.getName());
        address.setText(device.getAddress());

        return row;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View row = inflater.inflate(R.layout.bluetooth_devices, parent, false);

        BluetoothDevice device = devices.get(position);

        TextView name = row.findViewById(R.id.name_label);
        TextView address = row.findViewById(R.id.address_label);

        name.setText(device.getName());
        address.setText(device.getAddress());

        return row;
    }
}