import json, strutils
import agentio

proc getString*(node: JsonNode, key: string): string =
  let v = node[key]
  if v.isNil:
    return nil
  else:
    return v.str

proc getBool*(node: JsonNode, key: string, default: bool): bool =
  let v = node[key]
  if v.isNil:
    return default
  case v.kind:
    of JBool:
      return v.bval
    of JString:
      return v.str == "true"
    else:
      return default

proc getSubjson*(node: JsonNode, key: string): JsonNode =
  let v = node[key]
  if v.isNil:
    return nil
  else:
    return parseJson(v.str)

proc nullsafeJson*(data: string): auto =
  if data == nil:
    return newJNull()
  else:
    return %data
