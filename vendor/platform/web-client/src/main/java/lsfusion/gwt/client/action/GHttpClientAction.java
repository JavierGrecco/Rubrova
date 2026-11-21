package lsfusion.gwt.client.action;

import java.util.Map;

public class GHttpClientAction implements GAction {

    public String connectionString;
    public GExternalHttpMethod method;
    public Long timeout;
    public byte[] body;
    public Map<String, String> headers;

    @SuppressWarnings("UnusedDeclaration")
    public GHttpClientAction() {
    }

    public GHttpClientAction(GExternalHttpMethod method, String connectionString, Long timeout, byte[] body, Map<String, String> headers) {
        this.method = method;
        this.connectionString = connectionString;
        this.timeout = timeout;
        this.body = body;
        this.headers = headers;
    }

    @Override
    public Object dispatch(GActionDispatcher dispatcher) throws Throwable {
        return dispatcher.execute(this);
    }
}
