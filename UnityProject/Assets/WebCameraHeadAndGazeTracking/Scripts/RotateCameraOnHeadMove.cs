using UnityEngine;
using NetMQ;
using System.Globalization;
public class RotateCameraOnHeadMove : MonoBehaviour
{
    public Transform Target;
    private FaceDetector _faceDetector;
    private ScriptConnector _scriptConnector;

    public int MIN_Y_DETECTED_ROTATION = 8;
    public int MIN_X_DETECTED_ROTATION = 4;

    public float ROTATION_SPEED = 4f;
    public float Y_ROTATION_DISTANCE = 1f;
    public float X_ROTATION_DISTANCE = 0.2f;

    private float previousXRotation = 0;
    private float previousYRotation = 0;
    private float currentXRotation = 0;
    private float currentYRotation = 0;
    private float receivedXRotation = 0;
    private float receivedYRotation = 0;
    private int noRotationReceivedCount = 0;
    
    private void Awake()
    {
        _faceDetector = new FaceDetector(Application.dataPath);
        _scriptConnector = new ScriptConnector();
    }

    private void Update()
    {
        string message = _scriptConnector.ReceiveMessage();
        parseMessage(message);

        // Debug.Log("X: "+receivedXRotation+"   "+"Y: "+receivedYRotation);
        if (message != null)
        {
            noRotationReceivedCount = 0;
            if (receivedXRotation >= previousXRotation + MIN_X_DETECTED_ROTATION) // rotate down
            {
                currentXRotation = currentXRotation + X_ROTATION_DISTANCE;
                rotateCamera(currentXRotation, currentYRotation);
            } else if (receivedXRotation < previousXRotation - MIN_X_DETECTED_ROTATION) {
                currentXRotation = currentXRotation - X_ROTATION_DISTANCE; // rotate up
                rotateCamera(currentXRotation, currentYRotation);
            }

            if (receivedYRotation >= previousYRotation + MIN_Y_DETECTED_ROTATION) // rotate right
            {
                currentYRotation = currentYRotation + Y_ROTATION_DISTANCE;
                rotateCamera(previousXRotation, currentYRotation);
            } 
            else if (receivedYRotation < previousYRotation - MIN_Y_DETECTED_ROTATION) // rotate left
            {
                currentYRotation = currentYRotation - Y_ROTATION_DISTANCE;
                rotateCamera(previousXRotation, currentYRotation);
            }
        } 
        else { 
            noRotationReceivedCount++; 
            if (noRotationReceivedCount > 50) // if cannot detect face for 50 frames then recenter
            {
                if (currentYRotation != 0)
                {
                    if (currentYRotation > 1) {
                        currentYRotation -= 1;
                    rotateCamera(0, currentYRotation);
                    } 
                    else if (currentYRotation < -1)
                    {
                        currentYRotation +=1;
                        rotateCamera(0, currentYRotation);
                    }
                    else 
                    {
                        rotateCamera(0, 0);
                        currentYRotation = 0;
                        previousYRotation = 0;
                    }
                }
            }
        } 
    }

    private void rotateCamera(float xRotation, float yRotation)
    {
        this.transform.localRotation = Quaternion.Euler(xRotation * ROTATION_SPEED, yRotation * ROTATION_SPEED, 0);
        previousYRotation = currentYRotation;
        previousXRotation  = currentXRotation;
        receivedYRotation = 0;
        receivedXRotation = 0;
    }

    private void parseMessage(string message)
    {
        if (message != null)
        {
            try 
            {
                string[] receivedRotations = message.Split(null);
                this.receivedXRotation = float.Parse(receivedRotations[0], CultureInfo.InvariantCulture.NumberFormat);
                this.receivedYRotation = float.Parse(receivedRotations[1], CultureInfo.InvariantCulture.NumberFormat);
            }
            catch {
                Debug.LogError(message);
            }
        }
    }

    private void OnDestroy()
    {
        _scriptConnector.Destroy();
        _faceDetector.Destroy();
    }
}