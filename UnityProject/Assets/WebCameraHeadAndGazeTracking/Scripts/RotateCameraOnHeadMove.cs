using UnityEngine;
using NetMQ;
using System.Globalization;
public class RotateCameraOnHeadMove : MonoBehaviour
{
    private FaceDetector _faceDetector;
    private ScriptConnector _scriptConnector;
    public Transform Target;

    public int MIN_DETECTED_ROTATION = 8;
    public float ROTATION_SPEED = 1.5f;
    public float Y_ROTATION_DISTANCE = 1.5f;
    public float X_ROTATION_DISTANCE = 1.5f;

    private float previousXRotation = 0;
    private float previousYRotation = 0;
    private float currentXRotation = 0;
    private float currentYRotation = 0;
    private float receivedXRotation = 0;
    private float receivedYRotation = 0;
    private int currentNullRotationCount = 0;
    
    private void Awake()
    {
        _faceDetector = new FaceDetector(Application.dataPath);
        _scriptConnector = new ScriptConnector();
    }

    private void Update()
    {
        receiveAndParseMessage();

        Debug.Log("X: "+receivedXRotation+"   "+"Y: "+receivedYRotation);
        if (receivedYRotation != 0 && receivedXRotation != 0)
        {
            currentNullRotationCount = 0;

            if (receivedYRotation > -MIN_DETECTED_ROTATION && receivedYRotation < MIN_DETECTED_ROTATION)
            {
                if (receivedXRotation >= previousXRotation + MIN_DETECTED_ROTATION) // rotate up
                {
                    currentXRotation = currentXRotation + X_ROTATION_DISTANCE;
                    rotateCamera(currentXRotation, currentYRotation);
                } else if (receivedXRotation < previousXRotation - MIN_DETECTED_ROTATION) {
                    currentXRotation = currentXRotation - X_ROTATION_DISTANCE; // rotate down
                    rotateCamera(currentXRotation, currentYRotation);
                }  
            } 
            else if (receivedYRotation >= previousYRotation + MIN_DETECTED_ROTATION) // rotate right
            {
                currentYRotation = currentYRotation + Y_ROTATION_DISTANCE;
                rotateCamera(0, currentYRotation);
            } 
            else if (receivedYRotation < previousYRotation - MIN_DETECTED_ROTATION) // rotate left
            {
                currentYRotation = currentYRotation - Y_ROTATION_DISTANCE;
                rotateCamera(0, currentYRotation);
            }
        } 
        else { 
            currentNullRotationCount++; 
            if (currentNullRotationCount > 50) // if cannot detect face for 50 frames then recenter
            {
                if (currentYRotation != 0)
                {
                    if (currentYRotation > 1) {
                        currentYRotation -= 1;
                        currentXRotation -= 1;
                    rotateCamera(currentXRotation, currentYRotation);
                    } 
                    else if (currentYRotation < -1)
                    {
                        currentYRotation +=1;
                        currentXRotation += 1;
                        rotateCamera(currentXRotation, currentYRotation);
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

    private void receiveAndParseMessage()
    {
        string message = _scriptConnector.ReceiveMessage();

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