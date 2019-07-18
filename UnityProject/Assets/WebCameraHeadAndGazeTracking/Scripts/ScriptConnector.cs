using NetMQ;
using NetMQ.Sockets;
using AsyncIO;
using System;
public class ScriptConnector 
{
    private SubscriberSocket socket = null;
    public ScriptConnector()
    {
        ForceDotNet.Force();
        socket = new SubscriberSocket();
        UnityEngine.Debug.Log("Connecting unity with python script...");
        socket.Connect("tcp://localhost:5555");
        socket.Subscribe("");
        
    }
    public string ReceiveMessage() 
    {
        if (socket != null)
        {
            string message = "";
            if (socket.TryReceiveFrameString(out message)) {
                return message;
            }
        }
        return null;
    }

    public void Destroy() 
    {
        UnityEngine.Debug.Log("Disconecting...");
        socket.Close();
        NetMQConfig.Cleanup();
    }
}