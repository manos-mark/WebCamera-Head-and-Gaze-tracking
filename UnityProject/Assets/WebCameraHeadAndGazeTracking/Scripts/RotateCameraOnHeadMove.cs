using UnityEngine;
using NetMQ;
using System.Globalization;
public class RotateCameraOnHeadMove : MonoBehaviour
{
    private FaceDetector _faceDetector;
    private ScriptConnector _scriptConnector;
    public GameObject camera;

    private static int MIN_DETECTED_ROTATION = 4;
    private static int MAX_DETECTED_ROTATION = 10;
    private static float ROTATION_SPEED = 0.5f;

    private float previousYRotation = 0;
    private float currentYRotation = 0;
    private float headYRotation = 0;
    private int currentNullRotationCount = 0;
    
    private void Start()
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
                ++currentYRotation;
                rotateCamera(currentYRotation, ROTATION_SPEED);
                previousYRotation = currentYRotation;
            } 
            else if (headYRotation < previousYRotation - MIN_DETECTED_ROTATION) // rotate left
            {
                --currentYRotation;
                rotateCamera(currentYRotation, ROTATION_SPEED);
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
                   rotateCamera(currentYRotation, ROTATION_SPEED);
                } 
                else if (currentYRotation < -1)
                {
                    currentYRotation +=1;
                    rotateCamera(currentYRotation, ROTATION_SPEED);
                }
                else 
                {
                    rotateCamera(0, ROTATION_SPEED);
                    currentYRotation = 0;
                }
            }
        } 
    }

    private void rotateCamera(float yRotation, float rotationSpeed)
    {
        UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, yRotation, 0, 0);
        this.camera.transform.rotation =  Quaternion.Slerp(this.camera.transform.rotation, targetRotation, rotationSpeed *  Time.deltaTime);
    }

    private void OnDestroy()
    {
        _scriptConnector.Destroy();
        _faceDetector.Destroy();
    }
}