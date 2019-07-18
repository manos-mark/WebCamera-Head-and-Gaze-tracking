using UnityEngine;
using NetMQ;
using System.Globalization;
public class CameraRotationOnHeadMove : MonoBehaviour
{
    private FaceDetector _faceDetector;

    private ScriptConnector _scriptConnector;

    private float previousYRotation = 0;
    private float currentYRotation = 0;

    private int currentNullRotationCount = 0;
    
    private void Start()
    {
        _faceDetector = new FaceDetector(Application.dataPath);
        _scriptConnector = new ScriptConnector();
    }

    private static int MIN_DETECTED_ROTATION = 4;
    private static int MAX_DETECTED_ROTATION = 10;
    private static float ROTATION_SPEED = 0.3f;

    private void Update()
    {
        Camera cam = GameObject.Find("Camera").GetComponent<Camera>();
        string message = _scriptConnector.ReceiveMessage();

        if (message != null)
        {
            currentNullRotationCount = 0;
            this.currentYRotation = float.Parse(message, CultureInfo.InvariantCulture.NumberFormat);
            
            if (currentYRotation >= previousYRotation + MIN_DETECTED_ROTATION) // rotate right
            {
                // if (currentYRotation < previousYRotation + MAX_DETECTED_ROTATION)
                // {
                    UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, currentYRotation, 0, 0);
                    cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                    previousYRotation = targetRotation.y;
                // }
            } 
            else if (currentYRotation < previousYRotation - MIN_DETECTED_ROTATION) // rotate left
            {
                // Debug.Log(previousYRotation - MAX_DETECTED_ROTATION);
                // if ( (currentYRotation  > previousYRotation - MAX_DETECTED_ROTATION) || (currentYRotation  > MAX_DETECTED_ROTATION - previousYRotation) )
                // {
                    UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, currentYRotation, 0, 0);
                    cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                    previousYRotation = targetRotation.y;
                // }
            }
        } 
        else { 
            currentNullRotationCount++; 
            if (currentNullRotationCount > 50) // if cannot detect face for 50 frames then recenter
            {
                Debug.Log(currentYRotation);
                if (currentYRotation > 0) {
                    currentYRotation -= 1;
                } 
                else if (currentYRotation < 0)
                {
                    currentYRotation +=1;
                }
                UnityEngine.Quaternion targetRotation = new UnityEngine.Quaternion(0, currentYRotation, 0, 0);
                cam.transform.rotation =  Quaternion.Slerp(transform.rotation, targetRotation, ROTATION_SPEED *  Time.deltaTime);
                previousYRotation = 0;
            }
        } 
    }

    private void OnDestroy()
    {
        _scriptConnector.Destroy();
        _faceDetector.Destroy();
    }
}