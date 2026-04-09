import { executeFeature } from "../services/featureService.js";

export const runFeature = async (req, res) => {
  const featureId = req.params.id;

  try {
    const result = await executeFeature(featureId);
    const parsed = JSON.parse(result);
    res.json(parsed);

  } catch (err) {
    res.status(500).send("Error running feature");
  }
};