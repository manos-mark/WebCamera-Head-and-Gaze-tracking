using UnityEngine;
using NetMQ;
using System.Globalization;
public class RotateCameraOnHeadMove : MonoBehaviour
{
    private FaceDetector _faceDetector;

    private ScriptConnector _scriptConnector;

    private float previousYRotation = 0;
    private float currentYRotation = 0;
    private float receivedYRotation = 0;
    private int currentNullRotationCount = 0;
    
    private void Start()
    {
        _faceDetector = new FaceDetector(Application.dataPath);
        _scriptConnector = new ScriptConnector();
    }

    private static int MIN_DETECTED_ROTATION = 4;
    private static int MAX_DETECTED_ROTATION = 10;
    private static float ROTATION_SPEED = 0.5f;

    private void Update()
    {
        Camera cam = GameObject.Find("Camera").GetComponent<Camera>();
        string message = _scriptConnector.ReceiveMessage();

        if (message != null)
        {
            currentNullRotationCount = 0;
            this.receivedYRotation = float.Parse(message, CultureInfo.InvariantCulture.NumberFormat);
            
            if (receivedYRotation >= previousYRotation + MIN_DETECTED_ROTATION) // rotate right
            {

                UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, ++currentYRotation, 0, 0);
                cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                previousYRotation = targetRotation.y;
            } 
            else if (receivedYRotation < previousYRotation - MIN_DETECTED_ROTATION) // rotate left
            {
                UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, --currentYRotation, 0, 0);
                cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                previousYRotation = targetRotation.y;
            }
        } 
        else { 
            currentNullRotationCount++; 
            if (currentNullRotationCount > 50) // if cannot detect face for 50 frames then recenter
            {
                UnityEngine.Quaternion targetRotation;
                if (currentYRotation == 0) return;
                if (currentYRotation > 1) {
                    currentYRotation -= 1;
                    targetRotation = new UnityEngine.Quaternion(0, currentYRotation, 0, 0);
                    cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                } 
                else if (currentYRotation < -1)
                {
                    currentYRotation +=1;
                    targetRotation = new UnityEngine.Quaternion(0, currentYRotation, 0, 0);
                    cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                }
                else 
                {
                    targetRotation = new UnityEngine.Quaternion(0, 0, 0, 0);
                    cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                    currentYRotation = 0;
                }
            }
        } 
    }

    private void OnDestroy()
    {
        _scriptConnector.Destroy();
        _faceDetector.Destroy();
    }
}