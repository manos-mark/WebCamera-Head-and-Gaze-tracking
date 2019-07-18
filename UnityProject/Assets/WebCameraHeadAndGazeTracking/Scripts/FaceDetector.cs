using System.Diagnostics;
public class FaceDetector
{
    private Process process = null;

    public FaceDetector(string dataPath) 
    {
        ProcessStartInfo psi = new ProcessStartInfo();

        string mainProjectFolder = dataPath.Substring(0,dataPath.LastIndexOf(("UnityProject")));

        psi.FileName = mainProjectFolder + @"PythonFiles/Miniconda2/python.exe";
        psi.FileName = psi.FileName.Replace("/","\\");

        var script = mainProjectFolder + @"PythonFiles/HeadAndGazeTracking/track_head_and_gaze.py";
        script = script.Replace("/","\\");
        psi.Arguments = $"\"{script}\"";

        psi.UseShellExecute = false;
        psi.CreateNoWindow = true;

        process = Process.Start(psi);
    }

    public void Destroy()
    {
        if (process != null)
        {
            process.Kill();
        }
    }
}