import json, strutils
import agentio

proc getString*(node: PJsonNode, key: string): string =
  let v = node[key]
  if v.isNil:
    return nil
  else:
    return v.str

proc getBool*(node: PJsonNode, key: string, default: bool): bool =
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

proc getSubjson*(node: PJsonNode, key: string): PJsonNode =
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
