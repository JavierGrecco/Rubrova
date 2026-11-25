package lsfusion.base.remote;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;

public class ZipServerSocket extends ServerSocket {
    public ZipServerSocket(int port) throws IOException {
        super();
        String bindAddress = System.getProperty("lsfusion.rmi.bindAddress");
        if (bindAddress == null || bindAddress.trim().isEmpty()) {
            bind(new InetSocketAddress(port), 500);
        } else {
            bind(new InetSocketAddress(InetAddress.getByName(bindAddress.trim()), port), 500);
        }
    }

    public Socket accept() throws IOException {
        if (isClosed())
            throw new SocketException("Socket is closed");
        if (!isBound())
            throw new SocketException("Socket is not bound yet");

        Socket socket = new ZipSocket(null);
//        Socket socket = new Socket();
        implAccept(socket);
        return socket;
    }
}
