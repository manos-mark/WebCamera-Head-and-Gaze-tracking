using UnityEngine;
using NetMQ;
using System.Globalization;
public class RotateCameraOnHeadMove : MonoBehaviour
{
    private FaceDetector _faceDetector;
    private ScriptConnector _scriptConnector;
    public Transform Target;

    public int MIN_DETECTED_ROTATION = 4;
    public float ROTATION_SPEED = 1.5f;
    public float ROTATION_DISTANCE = 1.5f;

    private float previousYRotation = 0;
    private float currentYRotation = 0;
    private float headYRotation = 0;
    private int currentNullRotationCount = 0;
    
    private void Awake()
    {
        _faceDetector = new FaceDetector(Application.dataPath);
        _scriptConnector = new ScriptConnector();
    }

    private void Update()
    {
        string message = _scriptConnector.ReceiveMessage();

        if (message != null)
        {
            currentNullRotationCount = 0;
            this.headYRotation = float.Parse(message, CultureInfo.InvariantCulture.NumberFormat);
            
            if (headYRotation >= previousYRotation + MIN_DETECTED_ROTATION) // rotate right
            {
                currentYRotation = currentYRotation + ROTATION_DISTANCE;
                rotateCamera(currentYRotation);
                previousYRotation = currentYRotation;
            } 
            else if (headYRotation < previousYRotation - MIN_DETECTED_ROTATION) // rotate left
            {
                currentYRotation = currentYRotation - ROTATION_DISTANCE;
                rotateCamera(currentYRotation);
                previousYRotation = currentYRotation;
            }
        } 
        else { 
            currentNullRotationCount++; 
            if (currentNullRotationCount > 50) // if cannot detect face for 50 frames then recenter
            {
                if (currentYRotation == 0) return;
                if (currentYRotation > 1) {
                    currentYRotation -= 1;
                   rotateCamera(currentYRotation);
                } 
                else if (currentYRotation < -1)
                {
                    currentYRotation +=1;
                    rotateCamera(currentYRotation);
                }
                else 
                {
                    rotateCamera(0);
                    currentYRotation = 0;
                }
            }
        } 
    }

    private void rotateCamera(float yRotation)
    {
        UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, yRotation, 0, 0);
        this.transform.localRotation = Quaternion.Euler(0, yRotation * ROTATION_SPEED, 0);
    }

    private void OnDestroy()
    {
        _scriptConnector.Destroy();
        _faceDetector.Destroy();
    }
}