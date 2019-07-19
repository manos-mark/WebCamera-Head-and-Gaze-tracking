using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraFollowCar : MonoBehaviour
{
    public Transform follow;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    void LateUpdate() {
        transform.position = follow.position;
    }
}
